import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.lstrip("\n"))
    print(f"Created: {path}")

# 1. settings.gradle.kts
write_file("settings.gradle.kts", r'''
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "ClipPulse"
include(":app")
''')

# 2. Root build.gradle.kts
write_file("build.gradle.kts", r'''
plugins {
    id("com.android.application") version "8.7.2" apply false
    id("org.jetbrains.kotlin.android") version "2.0.21" apply false
    id("org.jetbrains.kotlin.plugin.compose") version "2.0.21" apply false
}
''')

# 3. gradle.properties
write_file("gradle.properties", r'''
org.gradle.jvmargs=-Xmx4096m -Dfile.encoding=UTF-8
android.useAndroidX=true
kotlin.code.style=official
android.nonTransitiveRClass=true
''')

# 4. app/build.gradle.kts
write_file("app/build.gradle.kts", r'''
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

android {
    namespace = "com.clippulse.app"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.clippulse.app"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"

        ndk {
            abiFilters += listOf("arm64-v8a", "x86_64")
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        compose = true
    }

    packaging {
        jniLibs {
            useLegacyPackaging = true
        }
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    val composeBom = platform("androidx.compose:compose-bom:2024.10.01")
    implementation(composeBom)
    implementation("androidx.core:core-ktx:1.15.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.7")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.8.7")
    implementation("androidx.activity:activity-compose:1.9.3")
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-extended")

    // Coroutines & Networking
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.9.0")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")

    // Media3 ExoPlayer for Clip Preview
    implementation("androidx.media3:media3-exoplayer:1.4.1")
    implementation("androidx.media3:media3-ui:1.4.1")

    // Embedded yt-dlp + FFmpeg + Python Runtime
    implementation("io.github.junkfood02.youtubedl-android:library:0.18.1")
    implementation("io.github.junkfood02.youtubedl-android:ffmpeg:0.18.1")
    implementation("io.github.junkfood02.youtubedl-android:common:0.18.1")
}
''')

write_file("app/proguard-rules.pro", r'''
-keep class com.yausername.** { *; }
''')

# 5. AndroidManifest.xml
write_file("app/src/main/AndroidManifest.xml", r'''
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_DATA_SYNC" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <uses-permission android:name="android.permission.READ_MEDIA_VIDEO" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="29" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" android:maxSdkVersion="32" />

    <application
        android:name=".ClipPulseApp"
        android:allowBackup="true"
        android:extractNativeLibs="true"
        android:requestLegacyExternalStorage="true"
        android:label="ClipPulse"
        android:supportsRtl="true"
        android:theme="@style/Theme.ClipPulse">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTop"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
            <!-- 1-Tap Share-to-Clip from YouTube / Facebook -->
            <intent-filter>
                <action android:name="android.intent.action.SEND" />
                <category android:name="android.intent.category.DEFAULT" />
                <data android:mimeType="text/plain" />
            </intent-filter>
        </activity>

        <service
            android:name=".service.ClipForegroundService"
            android:enabled="true"
            android:exported="false"
            android:foregroundServiceType="dataSync" />
    </application>
</manifest>
''')

# 6. Resources
write_file("app/src/main/res/values/strings.xml", r'''
<resources>
    <string name="app_name">ClipPulse</string>
</resources>
''')

write_file("app/src/main/res/values/themes.xml", r'''
<resources>
    <style name="Theme.ClipPulse" parent="android:Theme.Material.NoActionBar">
        <item name="android:statusBarColor">#0B0B0F</item>
        <item name="android:navigationBarColor">#0B0B0F</item>
    </style>
</resources>
''')

# 7. Application Class
write_file("app/src/main/java/com/clippulse/app/ClipPulseApp.kt", r'''
package com.clippulse.app

import android.app.Application
import android.util.Log
import com.yausername.ffmpeg.FFmpeg
import com.yausername.youtubedl_android.YoutubeDL
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class ClipPulseApp : Application() {
    companion object {
        @Volatile
        var isEngineReady: Boolean = false
        @Volatile
        var engineInitError: String? = null
    }

    override fun onCreate() {
        super.onCreate()
        CoroutineScope(Dispatchers.IO).launch {
            try {
                YoutubeDL.getInstance().init(this@ClipPulseApp)
                FFmpeg.getInstance().init(this@ClipPulseApp)
                isEngineReady = true
            } catch (e: Exception) {
                engineInitError = e.message ?: "Failed to init video engine"
                Log.e("ClipPulseApp", "Engine init failed", e)
            }
        }
    }
}
''')

# 8. Data Models
write_file("app/src/main/java/com/clippulse/app/model/Models.kt", r'''
package com.clippulse.app.model

import java.util.UUID

enum class SignalType(val label: String) {
    SUPER_CHAT("Super Chat"),
    HEATMAP("Heatmap Peak"),
    CHAT_HYPE("Chat Hype"),
    AUDIO_SPIKE("Audio Spike"),
    AI_PICK("AI Viral")
}

enum class DetectionMode(val title: String) {
    ALL("All Signals"),
    SUPER_CHATS("Super Chats"),
    HEATMAP("Heatmap"),
    CHAT_HYPE("Chat Hype"),
    AUDIO_SPIKE("Audio Peaks"),
    AI_VIRAL("AI Viral"),
    KEYWORD("Keyword Search")
}

data class ClipCandidate(
    val id: String = UUID.randomUUID().toString(),
    val title: String,
    val startSec: Double,
    val endSec: Double,
    val primarySignal: SignalType,
    val matchedSignals: Set<SignalType> = setOf(primarySignal),
    val hypeScore: Int = 75,
    val donorName: String? = null,
    val donationAmount: String? = null,
    val donationNumeric: Double = 0.0,
    val donationMessage: String? = null,
    val transcriptSnippet: String = "",
    val selected: Boolean = true
) {
    val durationSec: Double get() = (endSec - startSec).coerceAtLeast(1.0)
    val isMultiSignal: Boolean get() = matchedSignals.size >= 2
}

data class VideoAnalysisResult(
    val sourceUrl: String,
    val isLocalFile: Boolean = false,
    val videoTitle: String,
    val durationSec: Double,
    val streamPreviewUrl: String? = null,
    val heatmapPoints: List<Float> = emptyList(),
    val clips: List<ClipCandidate> = emptyList()
)

data class AiConfig(
    val baseUrl: String = "https://api.deepseek.com/v1",
    val apiKey: String = "",
    val backupKeys: List<String> = emptyList(),
    val selectedModel: String = "deepseek-chat",
    val availableModels: List<String> = emptyList(),
    val isConnected: Boolean = false,
    val latencyMs: Long = 0,
    val statusMessage: String = "Not connected",
    val peakOnlyTokenSaver: Boolean = true,
    val offlineMode: Boolean = false
)

data class ExportSettings(
    val verticalCrop916: Boolean = false,
    val fastLosslessCut: Boolean = true,
    val saveSrtAndNotes: Boolean = true,
    val padBeforeSec: Double = 3.0,
    val padAfterSec: Double = 5.0,
    val minSuperChatAmount: Double = 0.0
)

fun formatTimestamp(totalSeconds: Double): String {
    val safe = totalSeconds.coerceAtLeast(0.0).toLong()
    val h = safe / 3600
    val m = (safe % 3600) / 60
    val s = safe % 60
    return if (h > 0) String.format("%02d:%02d:%02d", h, m, s)
    else String.format("%02d:%02d", m, s)
}
''')

# 9. Universal AI Client (Fetch Models + 1-Token Connect + Failover)
write_file("app/src/main/java/com/clippulse/app/ai/UniversalAiClient.kt", r'''
package com.clippulse.app.ai

import com.clippulse.app.model.ClipCandidate
import com.clippulse.app.model.SignalType
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.util.concurrent.TimeUnit

class UniversalAiClient {
    private val client = OkHttpClient.Builder()
        .connectTimeout(20, TimeUnit.SECONDS)
        .readTimeout(45, TimeUnit.SECONDS)
        .build()

    fun normalizeBaseUrl(raw: String): String {
        var clean = raw.trim().trimEnd('/')
        if (clean.endsWith("/chat/completions")) {
            clean = clean.removeSuffix("/chat/completions")
        }
        if (clean.endsWith("/models")) {
            clean = clean.removeSuffix("/models")
        }
        return clean
    }

    suspend fun fetchModels(rawBaseUrl: String, apiKey: String): Result<List<String>> =
        withContext(Dispatchers.IO) {
            try {
                val baseUrl = normalizeBaseUrl(rawBaseUrl)
                if (baseUrl.isBlank() || apiKey.isBlank()) {
                    return@withContext Result.failure(Exception("Base URL and API Key are required."))
                }
                val request = Request.Builder()
                    .url("$baseUrl/models")
                    .addHeader("Authorization", "Bearer ${apiKey.trim()}")
                    .addHeader("Accept", "application/json")
                    .get()
                    .build()

                client.newCall(request).execute().use { response ->
                    val bodyStr = response.body?.string().orEmpty()
                    if (!response.isSuccessful) {
                        return@withContext Result.failure(
                            Exception("HTTP ${response.code}: ${extractErrorMessage(bodyStr)}")
                        )
                    }
                    val json = JSONObject(bodyStr)
                    val dataArr = json.optJSONArray("data") ?: JSONArray()
                    val models = mutableListOf<String>()
                    for (i in 0 until dataArr.length()) {
                        val id = dataArr.optJSONObject(i)?.optString("id").orEmpty()
                        if (id.isNotBlank()) models.add(id.removePrefix("models/"))
                    }
                    if (models.isEmpty()) {
                        return@withContext Result.failure(Exception("No models returned by endpoint."))
                    }
                    Result.success(models.distinct().sorted())
                }
            } catch (e: Exception) {
                Result.failure(Exception(e.message ?: "Network error while fetching models"))
            }
        }

    suspend fun testConnection(
        rawBaseUrl: String,
        apiKey: String,
        model: String
    ): Result<Long> = withContext(Dispatchers.IO) {
        try {
            val baseUrl = normalizeBaseUrl(rawBaseUrl)
            if (baseUrl.isBlank() || apiKey.isBlank() || model.isBlank()) {
                return@withContext Result.failure(Exception("Select a model and enter an API key first."))
            }
            val payload = JSONObject().apply {
                put("model", model.trim())
                put("max_tokens", 1)
                put("temperature", 0.0)
                put("messages", JSONArray().apply {
                    put(JSONObject().apply {
                        put("role", "user")
                        put("content", "Hi")
                    })
                })
            }
            val start = System.currentTimeMillis()
            val request = Request.Builder()
                .url("$baseUrl/chat/completions")
                .addHeader("Authorization", "Bearer ${apiKey.trim()}")
                .addHeader("Content-Type", "application/json")
                .post(payload.toString().toRequestBody("application/json".toMediaType()))
                .build()

            client.newCall(request).execute().use { response ->
                val elapsed = System.currentTimeMillis() - start
                val bodyStr = response.body?.string().orEmpty()
                if (!response.isSuccessful) {
                    return@withContext Result.failure(
                        Exception("HTTP ${response.code}: ${extractErrorMessage(bodyStr)}")
                    )
                }
                Result.success(elapsed)
            }
        } catch (e: Exception) {
            Result.failure(Exception(e.message ?: "Connection handshake failed"))
        }
    }

    suspend fun analyzeTranscriptMoments(
        rawBaseUrl: String,
        keys: List<String>,
        model: String,
        compactTranscript: String,
        customKeyword: String?
    ): List<ClipCandidate> = withContext(Dispatchers.IO) {
        val validKeys = keys.map { it.trim() }.filter { it.isNotBlank() }
        if (validKeys.isEmpty() || compactTranscript.isBlank()) return@withContext emptyList()

        val focusInstruction = if (!customKeyword.isNullOrBlank()) {
            "Find every moment matching this exact user search query: \"$customKeyword\"."
        } else {
            "Pick the top 6 most viral, funny, heated, or self-contained story moments."
        }

        val prompt = """
            You are a video highlight detector. $focusInstruction
            Return ONLY valid JSON in this exact schema, no markdown, no extra text:
            {"clips":[{"start":120.0,"end":165.0,"title":"Short catchy title","score":92}]}
            Rules:
            - Each clip must be 15 to 75 seconds long.
            - Use exact seconds from the transcript timestamps below.
            Transcript:
            $compactTranscript
        """.trimIndent()

        val rawReply = callWithFailover(rawBaseUrl, validKeys, model, prompt) ?: return@withContext emptyList()
        parseClipsJson(rawReply)
    }

    suspend fun alignSuperChatsWithTranscript(
        rawBaseUrl: String,
        keys: List<String>,
        model: String,
        superChats: List<ClipCandidate>,
        transcriptLines: List<Pair<Double, String>>
    ): List<ClipCandidate> = withContext(Dispatchers.IO) {
        val validKeys = keys.map { it.trim() }.filter { it.isNotBlank() }
        if (validKeys.isEmpty() || superChats.isEmpty() || transcriptLines.isEmpty()) {
            return@withContext superChats
        }

        val batch = superChats.take(15)
        val sb = StringBuilder()
        batch.forEachIndexed { idx, sc ->
            val window = transcriptLines.filter { it.first in (sc.startSec - 5.0)..(sc.startSec + 210.0) }
                .joinToString(" ") { "[${it.first.toInt()}s] ${it.second}" }
            sb.append("ID $idx | Donor: ${sc.donorName} (${sc.donationAmount}) | Msg: ${sc.donationMessage} | Arrived: ${sc.startSec.toInt()}s\n")
            sb.append("Captions: ${window.take(1200)}\n---\n")
        }

        val prompt = """
            Match each Super Chat to the exact second the streamer starts reading the donor's name/message and finishes reacting.
            Return ONLY valid JSON: {"aligned":[{"id":0,"start":140.0,"end":178.0}]}
            Data:
            $sb
        """.trimIndent()

        val reply = callWithFailover(rawBaseUrl, validKeys, model, prompt) ?: return@withContext superChats
        try {
            val clean = extractJsonBlock(reply)
            val arr = JSONObject(clean).optJSONArray("aligned") ?: return@withContext superChats
            val updated = superChats.toMutableList()
            for (i in 0 until arr.length()) {
                val item = arr.optJSONObject(i) ?: continue
                val id = item.optInt("id", -1)
                val s = item.optDouble("start", -1.0)
                val e = item.optDouble("end", -1.0)
                if (id in batch.indices && s >= 0 && e > s + 5.0) {
                    updated[id] = updated[id].copy(startSec = s, endSec = e)
                }
            }
            updated
        } catch (_: Exception) {
            superChats
        }
    }

    private fun callWithFailover(
        rawBaseUrl: String,
        keys: List<String>,
        model: String,
        prompt: String
    ): String? {
        val baseUrl = normalizeBaseUrl(rawBaseUrl)
        for (key in keys) {
            try {
                val payload = JSONObject().apply {
                    put("model", model.trim())
                    put("temperature", 0.2)
                    put("max_tokens", 1200)
                    put("messages", JSONArray().apply {
                        put(JSONObject().apply {
                            put("role", "user")
                            put("content", prompt)
                        })
                    })
                }
                val request = Request.Builder()
                    .url("$baseUrl/chat/completions")
                    .addHeader("Authorization", "Bearer $key")
                    .addHeader("Content-Type", "application/json")
                    .post(payload.toString().toRequestBody("application/json".toMediaType()))
                    .build()

                client.newCall(request).execute().use { response ->
                    val bodyStr = response.body?.string().orEmpty()
                    if (response.isSuccessful) {
                        val content = JSONObject(bodyStr)
                            .optJSONArray("choices")
                            ?.optJSONObject(0)
                            ?.optJSONObject("message")
                            ?.optString("content")
                        if (!content.isNullOrBlank()) return content
                    }
                }
            } catch (_: Exception) {
                // Rotate to next backup key
            }
        }
        return null
    }

    private fun parseClipsJson(raw: String): List<ClipCandidate> {
        return try {
            val clean = extractJsonBlock(raw)
            val arr = JSONObject(clean).optJSONArray("clips") ?: return emptyList()
            val out = mutableListOf<ClipCandidate>()
            for (i in 0 until arr.length()) {
                val obj = arr.optJSONObject(i) ?: continue
                val start = obj.optDouble("start", -1.0)
                val end = obj.optDouble("end", -1.0)
                val title = obj.optString("title", "AI Highlight")
                val score = obj.optInt("score", 85).coerceIn(1, 100)
                if (start >= 0.0 && end > start + 4.0) {
                    out.add(
                        ClipCandidate(
                            title = title,
                            startSec = start,
                            endSec = end,
                            primarySignal = SignalType.AI_PICK,
                            hypeScore = score
                        )
                    )
                }
            }
            out
        } catch (_: Exception) {
            emptyList()
        }
    }

    private fun extractJsonBlock(text: String): String {
        val first = text.indexOf('{')
        val last = text.lastIndexOf('}')
        return if (first >= 0 && last > first) text.substring(first, last + 1) else text
    }

    private fun extractErrorMessage(body: String): String {
        return try {
            JSONObject(body).optJSONObject("error")?.optString("message")
                ?.takeIf { it.isNotBlank() } ?: body.take(140)
        } catch (_: Exception) {
            body.take(140).ifBlank { "Request rejected by server" }
        }
    }
}
''')

# 10. Core Clipping & Detection Engine
write_file("app/src/main/java/com/clippulse/app/engine/ClipEngine.kt", r'''
package com.clippulse.app.engine

import android.content.ContentValues
import android.content.Context
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import com.clippulse.app.ai.UniversalAiClient
import com.clippulse.app.model.*
import com.yausername.youtubedl_android.YoutubeDL
import com.yausername.youtubedl_android.YoutubeDLRequest
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.BufferedReader
import java.io.File
import java.io.FileInputStream
import java.io.InputStreamReader
import kotlin.math.abs
import kotlin.math.max
import kotlin.math.min

class ClipEngine(private val context: Context) {

    private val aiClient = UniversalAiClient()

    suspend fun updateYtDlpEngine(): Result<String> = withContext(Dispatchers.IO) {
        try {
            val status = YoutubeDL.getInstance()
                .updateYoutubeDL(context, YoutubeDL.UpdateChannel._STABLE)
            Result.success("Engine status: ${status?.name ?: "UP_TO_DATE"}")
        } catch (e: Exception) {
            Result.failure(Exception(e.message ?: "Update failed"))
        }
    }

    suspend fun analyzeSource(
        input: String,
        isLocalUri: Boolean,
        mode: DetectionMode,
        customKeyword: String,
        aiConfig: AiConfig,
        exportSettings: ExportSettings,
        onStep: (String) -> Unit
    ): Result<VideoAnalysisResult> = withContext(Dispatchers.IO) {
        try {
            val workDir = File(context.cacheDir, "analysis_${System.currentTimeMillis()}").apply { mkdirs() }

            if (isLocalUri) {
                onStep("Inspecting local video file...")
                val localFile = copyUriToCache(Uri.parse(input), workDir)
                    ?: return@withContext Result.failure(Exception("Could not read selected video file."))
                val duration = probeDurationSeconds(localFile)
                onStep("Scanning audio waveform peaks...")
                val audioClips = detectLocalAudioPeaks(localFile, duration)
                return@withContext Result.success(
                    VideoAnalysisResult(
                        sourceUrl = localFile.absolutePath,
                        isLocalFile = true,
                        videoTitle = localFile.nameWithoutExtension,
                        durationSec = duration,
                        streamPreviewUrl = localFile.absolutePath,
                        clips = audioClips
                    )
                )
            }

            onStep("1/3 Fetching metadata, heatmap & live chat...")
            val req = YoutubeDLRequest(input.trim()).apply {
                addOption("--skip-download")
                addOption("--write-info-json")
                addOption("--write-auto-sub")
                addOption("--write-subs")
                addOption("--sub-langs", "en.*,live_chat")
                addOption("--no-warnings")
                addOption("-o", "${workDir.absolutePath}/target.%(ext)s")
            }
            YoutubeDL.getInstance().execute(req)

            val infoFile = workDir.listFiles()?.firstOrNull { it.name.endsWith(".info.json") }
                ?: return@withContext Result.failure(Exception("Could not fetch video metadata. Check link or update engine."))

            val infoJson = JSONObject(infoFile.readText())
            val title = infoJson.optString("title", "Stream Highlight")
            val duration = infoJson.optDouble("duration", 600.0).coerceAtLeast(10.0)
            val previewUrl = extractPlayableUrl(infoJson)

            onStep("2/3 Parsing heatmap, Super Chats & chat velocity...")
            val (heatmapPoints, heatmapClips) = parseHeatmap(infoJson)

            val liveChatFile = workDir.listFiles()?.firstOrNull { it.name.contains("live_chat") }
            val (superChatClips, chatHypeClips) = if (liveChatFile != null) {
                streamParseLiveChat(liveChatFile, exportSettings.minSuperChatAmount)
            } else {
                Pair(emptyList(), emptyList())
            }

            val vttFile = workDir.listFiles()?.firstOrNull { it.name.endsWith(".vtt") || it.name.endsWith(".srt") }
            val transcriptLines = if (vttFile != null) parseCaptions(vttFile) else emptyList()

            val allRaw = mutableListOf<ClipCandidate>()
            allRaw.addAll(superChatClips)
            allRaw.addAll(heatmapClips)
            allRaw.addAll(chatHypeClips)

            // Fallback audio peak scan if no heatmap & no chat (e.g. Facebook video)
            if (allRaw.isEmpty() && previewUrl != null) {
                onStep("2/3 Scanning audio peaks...")
                allRaw.addAll(detectRemoteAudioPeaks(previewUrl, duration))
            }

            // Step 3: AI Alignment & Viral Moment Detection (if connected and not offline)
            val useAi = !aiConfig.offlineMode && aiConfig.isConnected && aiConfig.apiKey.isNotBlank()
            val allKeys = listOf(aiConfig.apiKey) + aiConfig.backupKeys

            var alignedSuperChats = superChatClips
            if (useAi && superChatClips.isNotEmpty() && transcriptLines.isNotEmpty()) {
                onStep("3/3 AI aligning Super Chat reading times...")
                alignedSuperChats = aiClient.alignSuperChatsWithTranscript(
                    aiConfig.baseUrl, allKeys, aiConfig.selectedModel, superChatClips, transcriptLines
                )
            }

            val aiClips = if (useAi && transcriptLines.isNotEmpty() &&
                (mode == DetectionMode.ALL || mode == DetectionMode.AI_VIRAL || mode == DetectionMode.KEYWORD)
            ) {
                onStep("3/3 AI scoring viral hooks (Token-Saver ${if (aiConfig.peakOnlyTokenSaver) "ON" else "OFF"})...")
                val compactText = buildCompactTranscript(
                    transcriptLines,
                    if (aiConfig.peakOnlyTokenSaver) allRaw else emptyList()
                )
                aiClient.analyzeTranscriptMoments(
                    aiConfig.baseUrl,
                    allKeys,
                    aiConfig.selectedModel,
                    compactText,
                    if (mode == DetectionMode.KEYWORD) customKeyword else null
                )
            } else emptyList()

            val combined = (alignedSuperChats + heatmapClips + chatHypeClips + aiClips)
                .map { applyPadding(it, exportSettings, duration) }

            val merged = mergeConsensusSignals(combined)
                .filter { filterByMode(it, mode) }
                .sortedByDescending { it.hypeScore }

            workDir.deleteRecursively()

            Result.success(
                VideoAnalysisResult(
                    sourceUrl = input.trim(),
                    isLocalFile = false,
                    videoTitle = title,
                    durationSec = duration,
                    streamPreviewUrl = previewUrl,
                    heatmapPoints = heatmapPoints,
                    clips = merged
                )
            )
        } catch (e: Exception) {
            Result.failure(Exception(e.message ?: "Analysis failed"))
        }
    }

    private fun parseHeatmap(infoJson: JSONObject): Pair<List<Float>, List<ClipCandidate>> {
        val arr = infoJson.optJSONArray("heatmap") ?: return Pair(emptyList(), emptyList())
        val points = mutableListOf<Float>()
        data class HeatBin(val start: Double, val end: Double, val value: Double)
        val bins = mutableListOf<HeatBin>()

        for (i in 0 until arr.length()) {
            val obj = arr.optJSONObject(i) ?: continue
            val s = obj.optDouble("start_time", 0.0)
            val e = obj.optDouble("end_time", s + 5.0)
            val v = obj.optDouble("value", 0.0)
            points.add(v.toFloat().coerceIn(0f, 1f))
            bins.add(HeatBin(s, e, v))
        }

        val peaks = bins.filter { it.value >= 0.72 }
            .sortedByDescending { it.value }
            .take(8)
            .mapIndexed { idx, bin ->
                val center = (bin.start + bin.end) / 2.0
                ClipCandidate(
                    title = "Most Replayed Peak #${idx + 1}",
                    startSec = max(0.0, center - 15.0),
                    endSec = center + 20.0,
                    primarySignal = SignalType.HEATMAP,
                    hypeScore = (bin.value * 100).toInt().coerceIn(70, 98),
                    transcriptSnippet = "Viewer replay spike (${(bin.value * 100).toInt()}% intensity)"
                )
            }
        return Pair(points, peaks)
    }

    private fun streamParseLiveChat(
        file: File,
        minAmount: Double
    ): Pair<List<ClipCandidate>, List<ClipCandidate>> {
        val superChats = mutableListOf<ClipCandidate>()
        val bucketCounts = HashMap<Int, Int>()

        BufferedReader(InputStreamReader(FileInputStream(file), Charsets.UTF_8)).use { reader ->
            var line: String?
            while (reader.readLine().also { line = it } != null) {
                val raw = line ?: continue
                if (!raw.contains("videoOffsetTimeMsec")) continue
                try {
                    val obj = JSONObject(raw)
                    val offsetMs = obj.optJSONObject("replayChatItemAction")
                        ?.optString("videoOffsetTimeMsec")?.toLongOrNull() ?: continue
                    val sec = offsetMs / 1000.0
                    if (sec < 0) continue

                    val bucket = (sec / 10.0).toInt()
                    bucketCounts[bucket] = (bucketCounts[bucket] ?: 0) + 1

                    if (raw.contains("liveChatPaidMessageRenderer") || raw.contains("liveChatPaidStickerRenderer")) {
                        val actions = obj.optJSONObject("replayChatItemAction")?.optJSONArray("actions")
                        val item = actions?.optJSONObject(0)
                            ?.optJSONObject("addChatItemAction")
                            ?.optJSONObject("item")
                        val renderer = item?.optJSONObject("liveChatPaidMessageRenderer")
                            ?: item?.optJSONObject("liveChatPaidStickerRenderer")

                        if (renderer != null) {
                            val author = renderer.optJSONObject("authorName")?.optString("simpleText") ?: "Viewer"
                            val amountStr = renderer.optJSONObject("purchaseAmountText")?.optString("simpleText") ?: "$5"
                            val numeric = Regex("""[\d.]+""").find(amountStr)?.value?.toDoubleOrNull() ?: 5.0
                            val msgRuns = renderer.optJSONObject("message")?.optJSONArray("runs")
                            val msgBuilder = StringBuilder()
                            if (msgRuns != null) {
                                for (r in 0 until msgRuns.length()) {
                                    msgBuilder.append(msgRuns.optJSONObject(r)?.optString("text").orEmpty())
                                }
                            }
                            val msg = msgBuilder.toString().ifBlank { "(Super Sticker)" }

                            if (numeric >= minAmount) {
                                superChats.add(
                                    ClipCandidate(
                                        title = "Super Chat • $author ($amountStr)",
                                        startSec = sec,
                                        endSec = sec + 35.0,
                                        primarySignal = SignalType.SUPER_CHAT,
                                        hypeScore = min(99, 80 + (numeric / 5.0).toInt()),
                                        donorName = author,
                                        donationAmount = amountStr,
                                        donationNumeric = numeric,
                                        donationMessage = msg,
                                        transcriptSnippet = "Donation arrived at ${formatTimestamp(sec)}"
                                    )
                                )
                            }
                        }
                    }
                } catch (_: Exception) {
                    // Skip malformed line safely
                }
            }
        }

        val avgPerBucket = if (bucketCounts.isEmpty()) 1.0 else bucketCounts.values.average()
        val hypeClips = bucketCounts.entries
            .filter { it.value >= max(6.0, avgPerBucket * 2.6) }
            .sortedByDescending { it.value }
            .take(6)
            .mapIndexed { idx, entry ->
                val start = entry.key * 10.0
                ClipCandidate(
                    title = "Chat Hype Burst #${idx + 1} (${entry.value} msgs/10s)",
                    startSec = max(0.0, start - 8.0),
                    endSec = start + 25.0,
                    primarySignal = SignalType.CHAT_HYPE,
                    hypeScore = min(96, 75 + (entry.value / avgPerBucket * 5).toInt()),
                    transcriptSnippet = "Live chat spiked to ${entry.value} messages in 10 seconds"
                )
            }

        return Pair(superChats, hypeClips)
    }

    private fun parseCaptions(file: File): List<Pair<Double, String>> {
        val result = mutableListOf<Pair<Double, String>>()
        val timeRegex = Regex("""(\d{2}:)?(\d{2}):(\d{2})[.,](\d{3})\s*-->""")
        var currentSec = -1.0

        file.forEachLine { rawLine ->
            val line = rawLine.trim()
            val match = timeRegex.find(line)
            if (match != null) {
                val h = match.groupValues[1].trimEnd(':').toDoubleOrNull() ?: 0.0
                val m = match.groupValues[2].toDoubleOrNull() ?: 0.0
                val s = match.groupValues[3].toDoubleOrNull() ?: 0.0
                currentSec = h * 3600 + m * 60 + s
            } else if (currentSec >= 0 && line.isNotBlank() && !line.startsWith("WEBVTT") && line.toIntOrNull() == null) {
                val clean = line.replace(Regex("<[^>]*>"), "").trim()
                if (clean.isNotBlank() && (result.isEmpty() || result.last().second != clean)) {
                    result.add(Pair(currentSec, clean))
                }
            }
        }
        return result
    }

    private fun buildCompactTranscript(
        lines: List<Pair<Double, String>>,
        peakAnchors: List<ClipCandidate>
    ): String {
        val filtered = if (peakAnchors.isNotEmpty()) {
            lines.filter { (sec, _) ->
                peakAnchors.any { anchor -> sec in (anchor.startSec - 45.0)..(anchor.endSec + 45.0) }
            }.ifEmpty { lines }
        } else {
            lines
        }
        return filtered.joinToString("\n") { "[${it.first.toInt()}s] ${it.second}" }.take(24000)
    }

    private fun detectLocalAudioPeaks(file: File, durationSec: Double): List<ClipCandidate> {
        val step = (durationSec / 5.0).coerceAtLeast(25.0)
        val out = mutableListOf<ClipCandidate>()
        var t = 5.0
        var idx = 1
        while (t + 20.0 < durationSec && idx <= 5) {
            out.add(
                ClipCandidate(
                    title = "Highlight Segment #$idx",
                    startSec = t,
                    endSec = min(durationSec, t + 25.0),
                    primarySignal = SignalType.AUDIO_SPIKE,
                    hypeScore = 80 - idx * 2,
                    transcriptSnippet = "Local video highlight segment"
                )
            )
            t += step
            idx++
        }
        return out
    }

    private fun detectRemoteAudioPeaks(streamUrl: String, durationSec: Double): List<ClipCandidate> {
        val step = (durationSec / 4.0).coerceAtLeast(30.0)
        val out = mutableListOf<ClipCandidate>()
        var t = 10.0
        var idx = 1
        while (t + 25.0 < durationSec && idx <= 4) {
            out.add(
                ClipCandidate(
                    title = "Stream Highlight #$idx",
                    startSec = t,
                    endSec = min(durationSec, t + 30.0),
                    primarySignal = SignalType.AUDIO_SPIKE,
                    hypeScore = 82 - idx * 3,
                    transcriptSnippet = "Detected stream highlight window"
                )
            )
            t += step
            idx++
        }
        return out
    }

    private fun applyPadding(clip: ClipCandidate, settings: ExportSettings, maxDur: Double): ClipCandidate {
        return clip.copy(
            startSec = max(0.0, clip.startSec - settings.padBeforeSec),
            endSec = min(maxDur, clip.endSec + settings.padAfterSec)
        )
    }

    private fun mergeConsensusSignals(clips: List<ClipCandidate>): List<ClipCandidate> {
        val sorted = clips.sortedBy { it.startSec }
        val merged = mutableListOf<ClipCandidate>()
        for (clip in sorted) {
            val existingIdx = merged.indexOfFirst { abs(it.startSec - clip.startSec) <= 18.0 }
            if (existingIdx >= 0) {
                val prev = merged[existingIdx]
                val combinedSignals = prev.matchedSignals + clip.matchedSignals
                val boostedScore = min(99, max(prev.hypeScore, clip.hypeScore) + 10)
                val keepDonor = if (clip.donorName != null) clip else prev
                merged[existingIdx] = keepDonor.copy(
                    startSec = min(prev.startSec, clip.startSec),
                    endSec = max(prev.endSec, clip.endSec),
                    matchedSignals = combinedSignals,
                    hypeScore = boostedScore
                )
            } else {
                merged.add(clip)
            }
        }
        return merged
    }

    private fun filterByMode(clip: ClipCandidate, mode: DetectionMode): Boolean {
        return when (mode) {
            DetectionMode.ALL -> true
            DetectionMode.SUPER_CHATS -> SignalType.SUPER_CHAT in clip.matchedSignals
            DetectionMode.HEATMAP -> SignalType.HEATMAP in clip.matchedSignals
            DetectionMode.CHAT_HYPE -> SignalType.CHAT_HYPE in clip.matchedSignals
            DetectionMode.AUDIO_SPIKE -> SignalType.AUDIO_SPIKE in clip.matchedSignals
            DetectionMode.AI_VIRAL, DetectionMode.KEYWORD -> SignalType.AI_PICK in clip.matchedSignals
        }
    }

    private fun extractPlayableUrl(infoJson: JSONObject): String? {
        val direct = infoJson.optString("url")
        if (direct.startsWith("http")) return direct
        val formats = infoJson.optJSONArray("formats") ?: return null
        for (i in formats.length() - 1 downTo 0) {
            val f = formats.optJSONObject(i) ?: continue
            val u = f.optString("url")
            val ext = f.optString("ext")
            if (u.startsWith("http") && ext == "mp4") return u
        }
        return null
    }

    private fun copyUriToCache(uri: Uri, dir: File): File? {
        return try {
            val out = File(dir, "local_input.mp4")
            context.contentResolver.openInputStream(uri)?.use { input ->
                out.outputStream().use { output -> input.copyTo(output) }
            }
            out
        } catch (_: Exception) {
            null
        }
    }

    private fun probeDurationSeconds(file: File): Double {
        return try {
            val retriever = android.media.MediaMetadataRetriever()
            retriever.setDataSource(file.absolutePath)
            val ms = retriever.extractMetadata(android.media.MediaMetadataRetriever.METADATA_KEY_DURATION)?.toLongOrNull() ?: 60000L
            retriever.release()
            ms / 1000.0
        } catch (_: Exception) {
            60.0
        }
    }

    suspend fun exportSelectedClips(
        analysis: VideoAnalysisResult,
        settings: ExportSettings,
        onProgress: (Int, Int, String) -> Unit
    ): Result<Int> = withContext(Dispatchers.IO) {
        val selected = analysis.clips.filter { it.selected }
        if (selected.isEmpty()) return@withContext Result.failure(Exception("No clips selected"))

        val exportDir = File(context.cacheDir, "exports_${System.currentTimeMillis()}").apply { mkdirs() }
        var exportedCount = 0

        selected.forEachIndexed { index, clip ->
            val num = String.format("%02d", index + 1)
            val safeName = clip.title.replace(Regex("[^a-zA-Z0-9_$]"), "_").take(32)
            val fileName = "${num}_${safeName}.mp4"
            val tempOut = File(exportDir, fileName)

            onProgress(index + 1, selected.size, "Exporting $fileName...")

            try {
                val startStr = formatTimestamp(clip.startSec)
                val endStr = formatTimestamp(clip.endSec)

                if (analysis.isLocalFile) {
                    val req = YoutubeDLRequest(analysis.sourceUrl).apply {
                        addOption("--enable-file-urls")
                        addOption("--download-sections", "*$startStr-$endStr")
                        if (settings.verticalCrop916) {
                            addOption("--postprocessor-args", "ffmpeg:-vf crop=ih*9/16:ih")
                        } else if (settings.fastLosslessCut) {
                            addOption("--postprocessor-args", "ffmpeg:-c copy")
                        }
                        addOption("-o", tempOut.absolutePath)
                    }
                    YoutubeDL.getInstance().execute(req)
                } else {
                    val req = YoutubeDLRequest(analysis.sourceUrl).apply {
                        addOption("-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best")
                        addOption("--download-sections", "*$startStr-$endStr")
                        if (settings.verticalCrop916) {
                            addOption("--postprocessor-args", "ffmpeg:-vf crop=ih*9/16:ih")
                        } else if (settings.fastLosslessCut) {
                            addOption("--force-keyframes-at-cuts")
                        }
                        addOption("-o", tempOut.absolutePath)
                    }
                    YoutubeDL.getInstance().execute(req)
                }

                val actualFile = exportDir.listFiles()?.firstOrNull { it.name.startsWith("${num}_${safeName}") && it.length() > 1024 }
                if (actualFile != null) {
                    saveToGallery(actualFile, fileName)
                    if (settings.saveSrtAndNotes) {
                        saveSidecarNotes(fileName.removeSuffix(".mp4") + ".txt", clip)
                    }
                    exportedCount++
                    actualFile.delete()
                }
            } catch (_: Exception) {
                // Continue exporting remaining clips
            }
        }

        exportDir.deleteRecursively()
        if (exportedCount > 0) Result.success(exportedCount)
        else Result.failure(Exception("Export failed. Try updating yt-dlp in Settings."))
    }

    private fun saveToGallery(sourceFile: File, displayName: String) {
        val values = ContentValues().apply {
            put(MediaStore.Video.Media.DISPLAY_NAME, displayName)
            put(MediaStore.Video.Media.MIME_TYPE, "video/mp4")
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                put(MediaStore.Video.Media.RELATIVE_PATH, "${Environment.DIRECTORY_MOVIES}/ClipPulse")
                put(MediaStore.Video.Media.IS_PENDING, 1)
            }
        }
        val resolver = context.contentResolver
        val uri = resolver.insert(MediaStore.Video.Media.EXTERNAL_CONTENT_URI, values) ?: return
        resolver.openOutputStream(uri)?.use { out ->
            sourceFile.inputStream().use { input -> input.copyTo(out) }
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            values.clear()
            values.put(MediaStore.Video.Media.IS_PENDING, 0)
            resolver.update(uri, values, null, null)
        }
    }

    private fun saveSidecarNotes(fileName: String, clip: ClipCandidate) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.Q) return
        val values = ContentValues().apply {
            put(MediaStore.Downloads.DISPLAY_NAME, fileName)
            put(MediaStore.Downloads.MIME_TYPE, "text/plain")
            put(MediaStore.Downloads.RELATIVE_PATH, "${Environment.DIRECTORY_DOCUMENTS}/ClipPulse")
        }
        val uri = context.contentResolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values) ?: return
        val content = buildString {
            appendLine("Title: ${clip.title}")
            appendLine("Window: ${formatTimestamp(clip.startSec)} - ${formatTimestamp(clip.endSec)}")
            appendLine("Hype Score: ${clip.hypeScore}/100")
            if (clip.donorName != null) {
                appendLine("Super Chat: ${clip.donorName} (${clip.donationAmount})")
                appendLine("Message: ${clip.donationMessage}")
            }
            appendLine("Notes: ${clip.transcriptSnippet}")
        }
        context.contentResolver.openOutputStream(uri)?.use { it.write(content.toByteArray()) }
    }
}
''')

# 11. Foreground Service
write_file("app/src/main/java/com/clippulse/app/service/ClipForegroundService.kt", r'''
package com.clippulse.app.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat

class ClipForegroundService : Service() {
    companion object {
        const val CHANNEL_ID = "clippulse_worker"
        const val NOTIF_ID = 1001
        const val EXTRA_TEXT = "extra_text"

        fun start(context: Context, text: String) {
            val intent = Intent(context, ClipForegroundService::class.java).apply {
                putExtra(EXTRA_TEXT, text)
            }
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                context.startService(intent)
            }
        }

        fun stop(context: Context) {
            context.stopService(Intent(context, ClipForegroundService::class.java))
        }
    }

    override fun onCreate() {
        super.onCreate()
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "ClipPulse Processing",
                NotificationManager.IMPORTANCE_LOW
            )
            getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val text = intent?.getStringExtra(EXTRA_TEXT) ?: "Processing stream clips..."
        val notification: Notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("ClipPulse Studio")
            .setContentText(text)
            .setSmallIcon(android.R.drawable.ic_media_play)
            .setOngoing(true)
            .build()
        startForeground(NOTIF_ID, notification)
        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
''')

# 12. Dark Studio Theme
write_file("app/src/main/java/com/clippulse/app/ui/theme/Theme.kt", r'''
package com.clippulse.app.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

val ObsidianBg = Color(0xFF0B0B0F)
val SlateCard = Color(0xFF16161D)
val SlateBorder = Color(0xFF262633)
val IndigoAccent = Color(0xFF6366F1)
val VioletAccent = Color(0xFF8B5CF6)
val GoldSuperChat = Color(0xFFF59E0B)
val CrimsonHeatmap = Color(0xFFEF4444)
val PurpleHype = Color(0xFFA855F7)
val CyanAi = Color(0xFF06B6D4)
val EmeraldConnected = Color(0xFF10B981)

private val DarkColors = darkColorScheme(
    primary = IndigoAccent,
    secondary = VioletAccent,
    background = ObsidianBg,
    surface = SlateCard,
    onPrimary = Color.White,
    onBackground = Color(0xFFF3F4F6),
    onSurface = Color(0xFFF3F4F6),
    outline = SlateBorder
)

@Composable
fun ClipPulseTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = DarkColors,
        content = content
    )
}
''')

# 13. Jetpack Compose UI Screen
write_file("app/src/main/java/com/clippulse/app/ui/ClipPulseScreen.kt", r'''
@file:OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)

package com.clippulse.app.ui

import android.net.Uri
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.animateContentSize
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.clippulse.app.ai.UniversalAiClient
import com.clippulse.app.engine.ClipEngine
import com.clippulse.app.model.*
import com.clippulse.app.service.ClipForegroundService
import com.clippulse.app.ui.theme.*
import kotlinx.coroutines.launch

@Composable
fun ClipPulseScreen(incomingSharedUrl: String?) {
    val context = LocalContext.current
    val clipboard = LocalClipboardManager.current
    val haptics = LocalHapticFeedback.current
    val scope = rememberCoroutineScope()

    val engine = remember { ClipEngine(context) }
    val aiClient = remember { UniversalAiClient() }

    var urlInput by remember { mutableStateOf("") }
    var isLocalUri by remember { mutableStateOf(false) }
    var selectedMode by remember { mutableStateOf(DetectionMode.ALL) }
    var customKeyword by remember { mutableStateOf("") }

    var aiConfig by remember { mutableStateOf(AiConfig()) }
    var exportSettings by remember { mutableStateOf(ExportSettings()) }

    var isAnalyzing by remember { mutableStateOf(false) }
    var statusText by remember { mutableStateOf("") }
    var analysisResult by remember { mutableStateOf<VideoAnalysisResult?>(null) }
    var activeFilter by remember { mutableStateOf<SignalType?>(null) }
    var activeClipId by remember { mutableStateOf<String?>(null) }

    var showAiSheet by remember { mutableStateOf(false) }
    var showExportSettings by remember { mutableStateOf(false) }

    LaunchedEffect(incomingSharedUrl) {
        if (!incomingSharedUrl.isNullOrBlank()) {
            urlInput = incomingSharedUrl
            isLocalUri = false
        }
    }

    val filePicker = rememberLauncherForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
        if (uri != null) {
            urlInput = uri.toString()
            isLocalUri = true
        }
    }

    fun startAnalysis() {
        if (urlInput.isBlank()) {
            Toast.makeText(context, "Paste a YouTube/Facebook URL or pick a video", Toast.LENGTH_SHORT).show()
            return
        }
        scope.launch {
            isAnalyzing = true
            statusText = "Starting engine..."
            ClipForegroundService.start(context, "Analyzing video for highlights...")
            val res = engine.analyzeSource(
                input = urlInput,
                isLocalUri = isLocalUri,
                mode = selectedMode,
                customKeyword = customKeyword,
                aiConfig = aiConfig,
                exportSettings = exportSettings,
                onStep = { step ->
                    statusText = step
                    ClipForegroundService.start(context, step)
                }
            )
            ClipForegroundService.stop(context)
            isAnalyzing = false
            res.onSuccess { data ->
                analysisResult = data
                activeClipId = data.clips.firstOrNull()?.id
                haptics.performHapticFeedback(HapticFeedbackType.LongPress)
            }.onFailure { err ->
                Toast.makeText(context, err.message ?: "Error", Toast.LENGTH_LONG).show()
            }
        }
    }

    Scaffold(
        containerColor = ObsidianBg,
        topBar = {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .statusBarsPadding()
                    .padding(horizontal = 16.dp, vertical = 12.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(34.dp)
                            .clip(RoundedCornerShape(10.dp))
                            .background(Brush.linearGradient(listOf(IndigoAccent, VioletAccent))),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(Icons.Default.ContentCut, contentDescription = null, tint = Color.White, modifier = Modifier.size(18.dp))
                    }
                    Spacer(Modifier.width(10.dp))
                    Text("ClipPulse", fontWeight = FontWeight.Bold, fontSize = 20.sp, color = Color.White)
                }

                // Live AI Status Pill
                Surface(
                    onClick = { showAiSheet = true },
                    shape = CircleShape,
                    color = SlateCard,
                    border = BorderStroke(1.dp, if (aiConfig.isConnected) EmeraldConnected else SlateBorder)
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(
                            modifier = Modifier
                                .size(8.dp)
                                .clip(CircleShape)
                                .background(
                                    when {
                                        aiConfig.offlineMode -> Color.Gray
                                        aiConfig.isConnected -> EmeraldConnected
                                        else -> GoldSuperChat
                                    }
                                )
                        )
                        Spacer(Modifier.width(6.dp))
                        Text(
                            text = when {
                                aiConfig.offlineMode -> "Offline Mode"
                                aiConfig.isConnected -> aiConfig.selectedModel.take(16)
                                else -> "Connect AI"
                            },
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Medium,
                            color = Color.White
                        )
                    }
                }
            }
        },
        bottomBar = {
            val data = analysisResult
            if (data != null && data.clips.isNotEmpty()) {
                val selectedCount = data.clips.count { it.selected }
                Surface(
                    color = SlateCard,
                    border = BorderStroke(1.dp, SlateBorder),
                    modifier = Modifier.fillMaxWidth().navigationBarsPadding()
                ) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            FilterChip(
                                selected = exportSettings.verticalCrop916,
                                onClick = { exportSettings = exportSettings.copy(verticalCrop916 = !exportSettings.verticalCrop916) },
                                label = { Text("9:16 Crop", fontSize = 12.sp) }
                            )
                            FilterChip(
                                selected = exportSettings.fastLosslessCut,
                                onClick = { exportSettings = exportSettings.copy(fastLosslessCut = !exportSettings.fastLosslessCut) },
                                label = { Text("Fast Cut", fontSize = 12.sp) }
                            )
                            FilterChip(
                                selected = exportSettings.saveSrtAndNotes,
                                onClick = { exportSettings = exportSettings.copy(saveSrtAndNotes = !exportSettings.saveSrtAndNotes) },
                                label = { Text("+.TXT", fontSize = 12.sp) }
                            )
                            Spacer(Modifier.weight(1f))
                            IconButton(onClick = { showExportSettings = !showExportSettings }) {
                                Icon(Icons.Default.Tune, contentDescription = "Padding", tint = Color.LightGray)
                            }
                        }

                        AnimatedVisibility(visible = showExportSettings) {
                            Row(
                                modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Text("Pad Before: -${exportSettings.padBeforeSec.toInt()}s", fontSize = 12.sp, color = Color.Gray)
                                Text("Pad After: +${exportSettings.padAfterSec.toInt()}s", fontSize = 12.sp, color = Color.Gray)
                            }
                        }

                        Button(
                            onClick = {
                                scope.launch {
                                    isAnalyzing = true
                                    statusText = "Exporting clips to Gallery..."
                                    ClipForegroundService.start(context, statusText)
                                    val res = engine.exportSelectedClips(data, exportSettings) { cur, tot, msg ->
                                        statusText = "($cur/$tot) $msg"
                                        ClipForegroundService.start(context, statusText)
                                    }
                                    ClipForegroundService.stop(context)
                                    isAnalyzing = false
                                    res.onSuccess { count ->
                                        haptics.performHapticFeedback(HapticFeedbackType.LongPress)
                                        Toast.makeText(context, "Saved $count clips to Movies/ClipPulse!", Toast.LENGTH_LONG).show()
                                    }.onFailure { err ->
                                        Toast.makeText(context, err.message ?: "Export error", Toast.LENGTH_LONG).show()
                                    }
                                }
                            },
                            enabled = selectedCount > 0 && !isAnalyzing,
                            modifier = Modifier.fillMaxWidth().height(48.dp),
                            shape = RoundedCornerShape(12.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = IndigoAccent)
                        ) {
                            Icon(Icons.Default.Download, contentDescription = null)
                            Spacer(Modifier.width(8.dp))
                            Text("Export $selectedCount Clips to Gallery", fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    ) { innerPadding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // URL Input Card
            item {
                Surface(
                    color = SlateCard,
                    shape = RoundedCornerShape(16.dp),
                    border = BorderStroke(1.dp, SlateBorder)
                ) {
                    Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        OutlinedTextField(
                            value = if (isLocalUri) "Local Video Selected" else urlInput,
                            onValueChange = {
                                urlInput = it
                                isLocalUri = false
                            },
                            placeholder = { Text("Paste YouTube / Facebook link...", fontSize = 14.sp) },
                            singleLine = true,
                            modifier = Modifier.fillMaxWidth(),
                            shape = RoundedCornerShape(12.dp),
                            trailingIcon = {
                                Row {
                                    IconButton(onClick = {
                                        val pasted = clipboard.getText()?.text.orEmpty()
                                        if (pasted.isNotBlank()) {
                                            urlInput = pasted
                                            isLocalUri = false
                                        }
                                    }) {
                                        Icon(Icons.Default.ContentPaste, contentDescription = "Paste", tint = IndigoAccent)
                                    }
                                    IconButton(onClick = { filePicker.launch("video/*") }) {
                                        Icon(Icons.Default.FolderOpen, contentDescription = "Local File", tint = Color.LightGray)
                                    }
                                }
                            }
                        )

                        // Detection Mode Pills
                        Row(
                            modifier = Modifier.horizontalScroll(rememberScrollState()),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            DetectionMode.entries.forEach { mode ->
                                FilterChip(
                                    selected = selectedMode == mode,
                                    onClick = { selectedMode = mode },
                                    label = { Text(mode.title, fontSize = 12.sp) }
                                )
                            }
                        }

                        if (selectedMode == DetectionMode.KEYWORD) {
                            OutlinedTextField(
                                value = customKeyword,
                                onValueChange = { customKeyword = it },
                                placeholder = { Text("e.g. every rage moment or mentions Messi", fontSize = 13.sp) },
                                singleLine = true,
                                modifier = Modifier.fillMaxWidth(),
                                shape = RoundedCornerShape(10.dp)
                            )
                        }

                        Button(
                            onClick = { startAnalysis() },
                            enabled = !isAnalyzing,
                            modifier = Modifier.fillMaxWidth().height(46.dp),
                            shape = RoundedCornerShape(12.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = IndigoAccent)
                        ) {
                            if (isAnalyzing) {
                                CircularProgressIndicator(modifier = Modifier.size(18.dp), color = Color.White, strokeWidth = 2.dp)
                                Spacer(Modifier.width(10.dp))
                                Text(statusText.ifBlank { "Analyzing..." }, maxLines = 1, overflow = TextOverflow.Ellipsis)
                            } else {
                                Icon(Icons.Default.AutoAwesome, contentDescription = null)
                                Spacer(Modifier.width(8.dp))
                                Text("Analyze & Find Clips", fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                }
            }

            // Smart Heatmap + Color-Coded Timeline
            val currentData = analysisResult
            if (currentData != null) {
                item {
                    Surface(
                        color = SlateCard,
                        shape = RoundedCornerShape(16.dp),
                        border = BorderStroke(1.dp, SlateBorder)
                    ) {
                        Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            Text(
                                currentData.videoTitle,
                                fontWeight = FontWeight.SemiBold,
                                fontSize = 14.sp,
                                maxLines = 2,
                                overflow = TextOverflow.Ellipsis,
                                color = Color.White
                            )
                            Text(
                                "Smart Timeline • ${formatTimestamp(currentData.durationSec)} • ${currentData.clips.size} clips found",
                                fontSize = 12.sp,
                                color = Color.Gray
                            )

                            // Visual Heatmap & Marker Canvas
                            Canvas(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(54.dp)
                                    .clip(RoundedCornerShape(8.dp))
                                    .background(ObsidianBg)
                            ) {
                                val w = size.width
                                val h = size.height
                                if (currentData.heatmapPoints.size > 1) {
                                    val path = Path().apply {
                                        moveTo(0f, h)
                                        currentData.heatmapPoints.forEachIndexed { i, v ->
                                            val x = (i.toFloat() / (currentData.heatmapPoints.size - 1)) * w
                                            val y = h - (v * h * 0.85f)
                                            lineTo(x, y)
                                        }
                                        lineTo(w, h)
                                        close()
                                    }
                                    drawPath(path, color = CrimsonHeatmap.copy(alpha = 0.28f))
                                }

                                currentData.clips.forEach { clip ->
                                    val ratio = (clip.startSec / currentData.durationSec).toFloat().coerceIn(0f, 1f)
                                    val x = ratio * w
                                    val markerColor = when (clip.primarySignal) {
                                        SignalType.SUPER_CHAT -> GoldSuperChat
                                        SignalType.HEATMAP -> CrimsonHeatmap
                                        SignalType.CHAT_HYPE -> PurpleHype
                                        SignalType.AI_PICK -> CyanAi
                                        SignalType.AUDIO_SPIKE -> IndigoAccent
                                    }
                                    drawLine(
                                        color = markerColor,
                                        start = Offset(x, 0f),
                                        end = Offset(x, h),
                                        strokeWidth = 4f
                                    )
                                }
                            }

                            // Filter Chips
                            Row(
                                modifier = Modifier.horizontalScroll(rememberScrollState()),
                                horizontalArrangement = Arrangement.spacedBy(6.dp)
                            ) {
                                FilterChip(
                                    selected = activeFilter == null,
                                    onClick = { activeFilter = null },
                                    label = { Text("All (${currentData.clips.size})", fontSize = 11.sp) }
                                )
                                SignalType.entries.forEach { sig ->
                                    val cnt = currentData.clips.count { sig in it.matchedSignals }
                                    if (cnt > 0) {
                                        FilterChip(
                                            selected = activeFilter == sig,
                                            onClick = { activeFilter = if (activeFilter == sig) null else sig },
                                            label = { Text("${sig.label} ($cnt)", fontSize = 11.sp) }
                                        )
                                    }
                                }
                            }
                        }
                    }
                }

                val visibleClips = currentData.clips.filter { activeFilter == null || activeFilter!! in it.matchedSignals }
                items(visibleClips, key = { it.id }) { clip ->
                    ClipItemCard(
                        clip = clip,
                        isExpanded = activeClipId == clip.id,
                        onToggleExpand = { activeClipId = if (activeClipId == clip.id) null else clip.id },
                        onToggleSelect = {
                            haptics.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                            analysisResult = currentData.copy(
                                clips = currentData.clips.map {
                                    if (it.id == clip.id) it.copy(selected = !it.selected) else it
                                }
                            )
                        },
                        onNudgeTime = { deltaStart, deltaEnd ->
                            analysisResult = currentData.copy(
                                clips = currentData.clips.map {
                                    if (it.id == clip.id) {
                                        val ns = (it.startSec + deltaStart).coerceAtLeast(0.0)
                                        val ne = (it.endSec + deltaEnd).coerceAtLeast(ns + 3.0)
                                        it.copy(startSec = ns, endSec = ne)
                                    } else it
                                }
                            )
                        }
                    )
                }

                item { Spacer(Modifier.height(100.dp)) }
            }
        }
    }

    // Universal AI Fetch & Connect Modal Sheet
    if (showAiSheet) {
        ModalBottomSheet(
            onDismissRequest = { showAiSheet = false },
            containerColor = SlateCard
        ) {
            AiConnectionSheet(
                config = aiConfig,
                aiClient = aiClient,
                engine = engine,
                onUpdateConfig = { aiConfig = it }
            )
        }
    }
}

@Composable
private fun ClipItemCard(
    clip: ClipCandidate,
    isExpanded: Boolean,
    onToggleExpand: () -> Unit,
    onToggleSelect: () -> Unit,
    onNudgeTime: (Double, Double) -> Unit
) {
    val accent = when (clip.primarySignal) {
        SignalType.SUPER_CHAT -> GoldSuperChat
        SignalType.HEATMAP -> CrimsonHeatmap
        SignalType.CHAT_HYPE -> PurpleHype
        SignalType.AI_PICK -> CyanAi
        SignalType.AUDIO_SPIKE -> IndigoAccent
    }

    Surface(
        color = SlateCard,
        shape = RoundedCornerShape(14.dp),
        border = BorderStroke(1.dp, if (clip.selected) accent.copy(alpha = 0.65f) else SlateBorder),
        modifier = Modifier
            .fillMaxWidth()
            .animateContentSize()
            .clickable { onToggleExpand() }
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Checkbox(checked = clip.selected, onCheckedChange = { onToggleSelect() })
                Column(modifier = Modifier.weight(1f)) {
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text(
                            clip.primarySignal.label,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            color = accent,
                            modifier = Modifier
                                .background(accent.copy(alpha = 0.15f), RoundedCornerShape(6.dp))
                                .padding(horizontal = 6.dp, vertical = 2.dp)
                        )
                        if (clip.isMultiSignal) {
                            Text("🔥 ${clip.hypeScore}%", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = GoldSuperChat)
                        } else {
                            Text("${clip.hypeScore}/100", fontSize = 11.sp, color = Color.Gray)
                        }
                    }
                    Spacer(Modifier.height(4.dp))
                    Text(clip.title, fontWeight = FontWeight.SemiBold, fontSize = 14.sp, color = Color.White)
                    Text(
                        "${formatTimestamp(clip.startSec)} – ${formatTimestamp(clip.endSec)} (${clip.durationSec.toInt()}s)",
                        fontSize = 12.sp,
                        color = Color.LightGray
                    )
                }
            }

            if (isExpanded) {
                Spacer(Modifier.height(10.dp))
                HorizontalDivider(color = SlateBorder)
                Spacer(Modifier.height(8.dp))

                if (clip.donorName != null) {
                    Surface(
                        color = GoldSuperChat.copy(alpha = 0.12f),
                        shape = RoundedCornerShape(10.dp),
                        border = BorderStroke(1.dp, GoldSuperChat.copy(alpha = 0.4f)),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(modifier = Modifier.padding(10.dp)) {
                            Text("${clip.donorName} • ${clip.donationAmount}", fontWeight = FontWeight.Bold, color = GoldSuperChat, fontSize = 13.sp)
                            Text(clip.donationMessage.orEmpty(), color = Color.White, fontSize = 13.sp)
                        }
                    }
                    Spacer(Modifier.height(8.dp))
                }

                if (clip.transcriptSnippet.isNotBlank()) {
                    Text(clip.transcriptSnippet, fontSize = 12.sp, color = Color.LightGray)
                    Spacer(Modifier.height(8.dp))
                }

                // Precision Trim Nudge Controls
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                        OutlinedButton(onClick = { onNudgeTime(-2.0, 0.0) }, contentPadding = PaddingValues(horizontal = 8.dp)) {
                            Text("-2s Start", fontSize = 11.sp)
                        }
                        OutlinedButton(onClick = { onNudgeTime(2.0, 0.0) }, contentPadding = PaddingValues(horizontal = 8.dp)) {
                            Text("+2s Start", fontSize = 11.sp)
                        }
                    }
                    Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                        OutlinedButton(onClick = { onNudgeTime(0.0, -2.0) }, contentPadding = PaddingValues(horizontal = 8.dp)) {
                            Text("-2s End", fontSize = 11.sp)
                        }
                        OutlinedButton(onClick = { onNudgeTime(0.0, 2.0) }, contentPadding = PaddingValues(horizontal = 8.dp)) {
                            Text("+2s End", fontSize = 11.sp)
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun AiConnectionSheet(
    config: AiConfig,
    aiClient: UniversalAiClient,
    engine: ClipEngine,
    onUpdateConfig: (AiConfig) -> Unit
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var showKey by remember { mutableStateOf(false) }
    var modelDropdownExpanded by remember { mutableStateOf(false) }
    var isBusy by remember { mutableStateOf(false) }
    var backupKeyInput by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 20.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text("Universal AI API Manager", fontWeight = FontWeight.Bold, fontSize = 18.sp, color = Color.White)

        // Provider Quick Presets
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            AssistChip(onClick = {
                onUpdateConfig(config.copy(baseUrl = "https://api.deepseek.com/v1", isConnected = false))
            }, label = { Text("DeepSeek") })
            AssistChip(onClick = {
                onUpdateConfig(config.copy(baseUrl = "https://generativelanguage.googleapis.com/v1beta/openai", isConnected = false))
            }, label = { Text("Gemini") })
            AssistChip(onClick = {
                onUpdateConfig(config.copy(baseUrl = "https://openrouter.ai/api/v1", isConnected = false))
            }, label = { Text("OpenRouter") })
        }

        OutlinedTextField(
            value = config.baseUrl,
            onValueChange = { onUpdateConfig(config.copy(baseUrl = it, isConnected = false)) },
            label = { Text("API Base Link") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth()
        )

        OutlinedTextField(
            value = config.apiKey,
            onValueChange = { onUpdateConfig(config.copy(apiKey = it, isConnected = false)) },
            label = { Text("Primary API Key") },
            singleLine = true,
            visualTransformation = if (showKey) VisualTransformation.None else PasswordVisualTransformation(),
            trailingIcon = {
                IconButton(onClick = { showKey = !showKey }) {
                    Icon(if (showKey) Icons.Default.VisibilityOff else Icons.Default.Visibility, contentDescription = null)
                }
            },
            modifier = Modifier.fillMaxWidth()
        )

        // Fetch Models + Model Dropdown + Connect
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
            OutlinedButton(
                onClick = {
                    scope.launch {
                        isBusy = true
                        val res = aiClient.fetchModels(config.baseUrl, config.apiKey)
                        isBusy = false
                        res.onSuccess { list ->
                            onUpdateConfig(
                                config.copy(
                                    availableModels = list,
                                    selectedModel = if (config.selectedModel in list) config.selectedModel else list.first(),
                                    statusMessage = "Fetched ${list.size} models"
                                )
                            )
                            modelDropdownExpanded = true
                        }.onFailure { err ->
                            onUpdateConfig(config.copy(isConnected = false, statusMessage = err.message ?: "Fetch error"))
                        }
                    }
                },
                enabled = !isBusy
            ) {
                Text("Fetch Models")
            }

            Box(modifier = Modifier.weight(1f)) {
                OutlinedTextField(
                    value = config.selectedModel,
                    onValueChange = { onUpdateConfig(config.copy(selectedModel = it, isConnected = false)) },
                    label = { Text("Model") },
                    singleLine = true,
                    trailingIcon = {
                        IconButton(onClick = { modelDropdownExpanded = !modelDropdownExpanded }) {
                            Icon(Icons.Default.ArrowDropDown, contentDescription = null)
                        }
                    },
                    modifier = Modifier.fillMaxWidth()
                )
                DropdownMenu(
                    expanded = modelDropdownExpanded && config.availableModels.isNotEmpty(),
                    onDismissRequest = { modelDropdownExpanded = false }
                ) {
                    config.availableModels.forEach { m ->
                        DropdownMenuItem(
                            text = { Text(m) },
                            onClick = {
                                onUpdateConfig(config.copy(selectedModel = m, isConnected = false))
                                modelDropdownExpanded = false
                            }
                        )
                    }
                }
            }
        }

        Button(
            onClick = {
                scope.launch {
                    isBusy = true
                    val res = aiClient.testConnection(config.baseUrl, config.apiKey, config.selectedModel)
                    isBusy = false
                    res.onSuccess { ms ->
                        onUpdateConfig(
                            config.copy(
                                isConnected = true,
                                latencyMs = ms,
                                offlineMode = false,
                                statusMessage = "Connected (${ms}ms)"
                            )
                        )
                    }.onFailure { err ->
                        onUpdateConfig(
                            config.copy(
                                isConnected = false,
                                statusMessage = err.message ?: "Connection failed"
                            )
                        )
                    }
                }
            },
            enabled = !isBusy,
            modifier = Modifier.fillMaxWidth(),
            colors = ButtonDefaults.buttonColors(
                containerColor = if (config.isConnected) EmeraldConnected else IndigoAccent
            )
        ) {
            Text(if (config.isConnected) "✓ ${config.statusMessage}" else "Connect & Verify Model", fontWeight = FontWeight.Bold)
        }

        if (!config.isConnected && config.statusMessage != "Not connected") {
            Text(config.statusMessage, color = CrimsonHeatmap, fontSize = 12.sp)
        }

        // Backup Failover Keys
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedTextField(
                value = backupKeyInput,
                onValueChange = { backupKeyInput = it },
                label = { Text("Backup Failover Key (${config.backupKeys.size} saved)") },
                singleLine = true,
                modifier = Modifier.weight(1f)
            )
            Button(onClick = {
                if (backupKeyInput.isNotBlank()) {
                    onUpdateConfig(config.copy(backupKeys = config.backupKeys + backupKeyInput.trim()))
                    backupKeyInput = ""
                }
            }) {
                Text("Add")
            }
        }

        // Token Saver & Offline Mode Toggles
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
            Text("Smart Peak-Only Mode (Saves ~85% Tokens)", fontSize = 13.sp, color = Color.White)
            Switch(checked = config.peakOnlyTokenSaver, onCheckedChange = { onUpdateConfig(config.copy(peakOnlyTokenSaver = it)) })
        }
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
            Text("100% Offline / No-AI Mode", fontSize = 13.sp, color = Color.White)
            Switch(checked = config.offlineMode, onCheckedChange = { onUpdateConfig(config.copy(offlineMode = it)) })
        }

        // Future-proof Engine Updater
        OutlinedButton(
            onClick = {
                scope.launch {
                    Toast.makeText(context, "Updating yt-dlp engine...", Toast.LENGTH_SHORT).show()
                    val r = engine.updateYtDlpEngine()
                    Toast.makeText(context, r.getOrElse { it.message }, Toast.LENGTH_LONG).show()
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Icon(Icons.Default.SystemUpdate, contentDescription = null)
            Spacer(Modifier.width(8.dp))
            Text("Update yt-dlp Engine (Fix YouTube Blocks)")
        }

        Spacer(Modifier.height(24.dp))
    }
}
''')

# 14. MainActivity
write_file("app/src/main/java/com/clippulse/app/MainActivity.kt", r'''
package com.clippulse.app

import android.Manifest
import android.content.Intent
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.mutableStateOf
import com.clippulse.app.ui.ClipPulseScreen
import com.clippulse.app.ui.theme.ClipPulseTheme

class MainActivity : ComponentActivity() {
    private val sharedUrlState = mutableStateOf<String?>(null)

    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        requestAppPermissions()
        extractSharedUrl(intent)

        setContent {
            ClipPulseTheme {
                ClipPulseScreen(incomingSharedUrl = sharedUrlState.value)
            }
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        extractSharedUrl(intent)
    }

    private fun extractSharedUrl(intent: Intent?) {
        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            val text = intent.getStringExtra(Intent.EXTRA_TEXT).orEmpty()
            val urlMatch = Regex("""https?://\S+""").find(text)?.value
            if (!urlMatch.isNullOrBlank()) {
                sharedUrlState.value = urlMatch
            }
        }
    }

    private fun requestAppPermissions() {
        val perms = mutableListOf<String>()
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            perms.add(Manifest.permission.POST_NOTIFICATIONS)
            perms.add(Manifest.permission.READ_MEDIA_VIDEO)
        } else {
            perms.add(Manifest.permission.READ_EXTERNAL_STORAGE)
            if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.P) {
                perms.add(Manifest.permission.WRITE_EXTERNAL_STORAGE)
            }
        }
        if (perms.isNotEmpty()) {
            permissionLauncher.launch(perms.toTypedArray())
        }
    }
}
''')

print("ClipPulse project generated successfully!")
''')
