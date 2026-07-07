import QtQuick
import QtCore
import org.kde.plasma.plasmoid

WallpaperItem {
	id: root

	// Runtime configuration, loaded from ~/.config/matrixia.conf.
	property string matrixMode: "normal"
	property string matrixColor: "#00ff00"
	property string backgroundColor: "#000000"
	property string matrixFontFamily: "VL Gothic"
	property int matrixFontSize: 21
	property int trailLength: 35
	property int frameInterval: 25
	property int spawnPerFrame: 1
	property int maxStreams: 256
	property int cycleFrames: 8
	property bool reverseDirection: false

	// Animation state.
	property var streams: []
	property int frameCounter: 0
	property var sessionRandomColor: randomColor()
	property bool clearRequested: true

	readonly property string katakana:
		"アイウエオカキクケコサシスセソタチツテト" +
		"ナニヌネノハヒフヘホマミムメモヤユヨ" +
		"ラリルレロワヰヱヲン"

	readonly property var palette: [
		"#ffffff", "#0000ff", "#000000", "#00ff00",
		"#ff7300", "#ffff00", "#ff0000", "#141432",
		"#ff00ff", "#800080", "#00ffff"
	]

	accentColor: matrixColor
	loading: false

	Settings {
		id: configFile
		location: StandardPaths.writableLocation(
			StandardPaths.ConfigLocation
		) + "/matrixia.conf"
		category: "Matrixia"
	}

	function boolValue(value, fallback) {
		if (value === undefined || value === null) {
			return fallback
		}

		const text = String(value).trim().toLowerCase()
		if (["1", "true", "yes", "on"].indexOf(text) >= 0) {
			return true
		}
		if (["0", "false", "no", "off"].indexOf(text) >= 0) {
			return false
		}
		return fallback
	}

	function intValue(value, fallback, minimum, maximum) {
		const parsed = parseInt(value, 10)
		if (isNaN(parsed)) {
			return fallback
		}
		return Math.max(minimum, Math.min(maximum, parsed))
	}

	function configuredMode() {
		if (boolValue(configFile.value("partymode", "off"), false)) {
			return "party"
		}
		if (boolValue(configFile.value("grayscale", "off"), false)) {
			return "grayscale"
		}
		if (boolValue(configFile.value("cyclist", "off"), false)) {
			return "cycle"
		}
		if (boolValue(configFile.value("random", "off"), false)) {
			return "random"
		}
		if (boolValue(configFile.value("doubletrouble", "off"), false)) {
			return "double"
		}

		const requested = String(
			configFile.value("mode", "normal")
		).trim().toLowerCase()

		const allowed = [
			"normal", "party", "grayscale", "cycle", "random", "double"
		]
		return allowed.indexOf(requested) >= 0 ? requested : "normal"
	}

	function reloadConfiguration() {
		configFile.sync()

		const newMode = configuredMode()
		const newColor = String(configFile.value("color", "#00ff00")).trim()
		const newBackground = String(
			configFile.value("background", "#000000")
		).trim()
		const newFontFamily = String(
			configFile.value("font", "VL Gothic")
		).trim()
		const newFontSize = intValue(
			configFile.value("font_size", 21), 21, 6, 120
		)
		const newTrailLength = intValue(
			configFile.value("trail", 35), 35, 2, 300
		)
		const newFrameInterval = intValue(
			configFile.value("frame_interval", 25), 25, 8, 1000
		)
		const newSpawnPerFrame = intValue(
			configFile.value("spawn_per_frame", 1), 1, 0, 20
		)
		const newMaxStreams = intValue(
			configFile.value("max_streams", 256), 256, 1, 5000
		)
		const newCycleFrames = intValue(
			configFile.value("cycle_frames", 8), 8, 1, 1000
		)
		const newReverse = boolValue(
			configFile.value("reverse", "off"), false
		)

		const resetNeeded =
			newMode !== matrixMode ||
			newColor !== matrixColor ||
			newFontSize !== matrixFontSize ||
			newFontFamily !== matrixFontFamily ||
			newBackground !== backgroundColor ||
			newReverse !== reverseDirection

		if (newMode === "random" && matrixMode !== "random") {
			sessionRandomColor = randomColor()
		}

		matrixMode = newMode
		matrixColor = newColor
		backgroundColor = newBackground
		matrixFontFamily = newFontFamily
		matrixFontSize = newFontSize
		trailLength = newTrailLength
		frameInterval = newFrameInterval
		spawnPerFrame = newSpawnPerFrame
		maxStreams = newMaxStreams
		cycleFrames = newCycleFrames
		reverseDirection = newReverse

		if (resetNeeded) {
			resetAnimation()
		}
	}

	function resetAnimation() {
		streams = []
		frameCounter = 0
		clearRequested = true
		matrixCanvas.requestPaint()
	}

	function randomColor() {
		return Qt.rgba(Math.random(), Math.random(), Math.random(), 1.0)
	}

	function randomCharacter() {
		if (Math.random() < 0.5) {
			return katakana.charAt(
				Math.floor(Math.random() * katakana.length)
			)
		}

		// Same approximate ASCII range as the original Python version.
		return String.fromCharCode(60 + Math.floor(Math.random() * 63))
	}

	function canvasFontFamily() {
		// Context2D uses CSS-like font syntax. Qt accepts double-quoted
		// family names reliably; the earlier single-quoted form could be
		// rejected, leaving the default 10px sans-serif font active.
		return String(matrixFontFamily)
			.trim()
			.replace(/\\/g, "\\\\")
			.replace(/"/g, '\\"')
	}

	function applyCanvasFont(context) {
		const requested =
			matrixFontSize + 'px "' + canvasFontFamily() + '"'

		context.font = requested

		// An invalid Context2D font assignment is silently ignored. If Qt
		// kept its default 10px font, retain the requested size and fall
		// back only to the generic monospace family.
		if (String(context.font).indexOf(matrixFontSize + "px") < 0) {
			context.font = matrixFontSize + "px monospace"
		}
	}

	function cellWidth() {
		return Math.max(6, Math.round(matrixFontSize * 0.9))
	}

	function spawnStream() {
		if (matrixCanvas.width <= 0 || matrixCanvas.height <= 0) {
			return
		}

		const columns = Math.max(
			1,
			Math.floor(matrixCanvas.width / cellWidth())
		)
		const column = Math.floor(Math.random() * columns)

		streams.push({
			x: column * cellWidth(),
			y: reverseDirection
				? matrixCanvas.height + matrixFontSize
				: -matrixFontSize,
			previous: null
		})
	}

	function foregroundColor() {
		switch (matrixMode) {
		case "party":
			return palette[Math.floor(Math.random() * palette.length)]
		case "grayscale":
			return "#ffffff"
		case "cycle":
			return palette[
				Math.floor(frameCounter / cycleFrames) % palette.length
			]
		case "random":
			return sessionRandomColor
		case "double":
			return randomColor()
		default:
			return matrixColor
		}
	}

	function drawGlyph(context, glyph, isHead) {
		if (glyph.background !== null) {
			context.fillStyle = glyph.background
			context.fillRect(
				glyph.x,
				glyph.y,
				cellWidth(),
				matrixFontSize
			)
		}

		context.fillStyle = glyph.foreground
		context.fillText(glyph.character, glyph.x, glyph.y)

		// The leading character is white, matching the original Descender.
		if (isHead) {
			context.fillStyle = "#ffffff"
			context.fillText(glyph.character, glyph.x, glyph.y)
		}
	}

	function paintFrame(context) {
		if (clearRequested) {
			context.globalAlpha = 1.0
			context.fillStyle = backgroundColor
			context.fillRect(
				0, 0, matrixCanvas.width, matrixCanvas.height
			)
			clearRequested = false
		}

		// Fade old glyphs close to one 8-bit intensity step after exactly
		// trailLength frames. The old 3/trailLength approximation left a
		// long exponential after-image which looked like screen burn-in.
		const fadeAlpha = Math.max(
			0.02,
			Math.min(0.85,
				1.0 - Math.pow(1.0 / 255.0, 1.0 / trailLength)
			)
		)

		context.save()
		context.globalCompositeOperation = "source-over"
		context.globalAlpha = fadeAlpha
		context.fillStyle = backgroundColor
		context.fillRect(
			0, 0, matrixCanvas.width, matrixCanvas.height
		)
		context.restore()

		applyCanvasFont(context)
		context.textBaseline = "top"

		let count = spawnPerFrame
		if (matrixMode === "double") {
			count *= 2
		}

		for (let i = 0; i < count && streams.length < maxStreams; ++i) {
			spawnStream()
		}

		const survivors = []
		const direction = reverseDirection ? -1 : 1

		for (let i = 0; i < streams.length; ++i) {
			const stream = streams[i]

			// Repaint the former white head in its actual trail colour.
			if (stream.previous !== null) {
				drawGlyph(context, stream.previous, false)
			}

			const glyph = {
				x: stream.x,
				y: stream.y,
				character: randomCharacter(),
				foreground: foregroundColor(),
				background: matrixMode === "double" ? randomColor() : null
			}

			drawGlyph(context, glyph, true)
			stream.previous = glyph
			stream.y += direction * matrixFontSize

			const stillVisible = reverseDirection
				? stream.y >= -matrixFontSize
				: stream.y <= matrixCanvas.height + matrixFontSize

			if (stillVisible) {
				survivors.push(stream)
			}
		}

		streams = survivors
		frameCounter += 1
		context.globalAlpha = 1.0
	}

	Canvas {
		id: matrixCanvas
		anchors.fill: parent
		antialiasing: false

		onPaint: root.paintFrame(getContext("2d"))
		onWidthChanged: root.resetAnimation()
		onHeightChanged: root.resetAnimation()
	}

	Timer {
		id: animationTimer
		interval: root.frameInterval
		running: true
		repeat: true
		onTriggered: matrixCanvas.requestPaint()
	}

	Timer {
		interval: 1000
		running: true
		repeat: true
		onTriggered: root.reloadConfiguration()
	}

	Component.onCompleted: {
		console.info("Matrixia configuration:", configFile.location)
		reloadConfiguration()
		resetAnimation()
	}
}
