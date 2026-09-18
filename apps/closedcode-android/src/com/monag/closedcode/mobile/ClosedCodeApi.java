package com.monag.closedcode.mobile;

import android.os.Handler;
import android.os.Looper;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public final class ClosedCodeApi {
    public interface Callback {
        void success(String body);
        void failure(String message);
    }

    public interface EventListener {
        void event(String data);
        void closed(String reason);
    }

    private final ExecutorService pool = Executors.newFixedThreadPool(4);
    private final Handler main = new Handler(Looper.getMainLooper());
    private volatile String baseUrl;
    private volatile boolean eventLoop;
    private volatile HttpURLConnection eventConnection;

    public ClosedCodeApi(String baseUrl) {
        setBaseUrl(baseUrl);
    }

    public void setBaseUrl(String value) {
        String v = value == null ? "" : value.trim();
        while (v.endsWith("/")) v = v.substring(0, v.length() - 1);
        this.baseUrl = v.isEmpty() ? "http://127.0.0.1:4096" : v;
    }

    public String getBaseUrl() {
        return baseUrl;
    }

    public void health(Callback cb) {
        async("GET", "/global/health", null, cb);
    }

    public void listSessions(String directory, Callback cb) {
        async("GET", "/session?" + routing(directory), null, cb);
    }

    public void createSession(String directory, Callback cb) {
        async("POST", "/session?" + routing(directory), null, cb);
    }

    public void createSession(String directory, String title, Callback cb) {
        try {
            JSONObject body = new JSONObject();
            if (title != null && !title.trim().isEmpty()) body.put("title", title.trim());
            async("POST", "/session?" + routing(directory), body.toString(), cb);
        } catch (Exception e) {
            main.post(() -> cb.failure(e.toString()));
        }
    }

    public void updateSessionTitle(String sessionId, String directory, String title, Callback cb) {
        try {
            JSONObject body = new JSONObject();
            body.put("title", title == null ? "" : title.trim());
            async("PATCH", "/session/" + enc(sessionId) + "?" + routing(directory), body.toString(), cb);
        } catch (Exception e) {
            main.post(() -> cb.failure(e.toString()));
        }
    }

    public void deleteSession(String sessionId, String directory, Callback cb) {
        async("DELETE", "/session/" + enc(sessionId) + "?" + routing(directory), null, cb);
    }

    public void listAgents(String directory, Callback cb) {
        async("GET", "/agent?" + routing(directory), null, cb);
    }

    public void listProviders(String directory, Callback cb) {
        async("GET", "/provider?" + routing(directory), null, cb);
    }

    public void messages(String sessionId, String directory, Callback cb) {
        async("GET", "/session/" + enc(sessionId) + "/message?" + routing(directory) + "&limit=100", null, cb);
    }

    public void promptAsync(String sessionId, String directory, String text, Callback cb) {
        promptAsync(sessionId, directory, text, null, null, cb);
    }

    public void promptAsync(String sessionId, String directory, String text, String providerId, String modelId, Callback cb) {
        promptAsync(sessionId, directory, text, providerId, modelId, null, null, cb);
    }

    public void promptAsync(String sessionId, String directory, String text, String providerId, String modelId, String agent, String variant, Callback cb) {
        try {
            JSONObject body = new JSONObject();
            JSONArray parts = new JSONArray();
            JSONObject part = new JSONObject();
            part.put("type", "text");
            part.put("text", text);
            parts.put(part);
            body.put("parts", parts);
            if (providerId != null && !providerId.trim().isEmpty() && modelId != null && !modelId.trim().isEmpty()) {
                JSONObject model = new JSONObject();
                model.put("providerID", providerId);
                model.put("modelID", modelId);
                body.put("model", model);
            }
            if (agent != null && !agent.trim().isEmpty()) body.put("agent", agent.trim());
            if (variant != null && !variant.trim().isEmpty()) body.put("variant", variant.trim());
            async("POST", "/session/" + enc(sessionId) + "/prompt_async?" + routing(directory), body.toString(), cb);
        } catch (Exception e) {
            main.post(() -> cb.failure(e.toString()));
        }
    }

    public void passthroughPrompt(String sessionId, String text, String providerId, String modelId, Callback cb) {
        try {
            JSONObject body = new JSONObject();
            body.put("providerID", providerId);
            body.put("model", modelId);
            body.put("sessionID", sessionId);
            JSONArray messages = new JSONArray();
            JSONObject message = new JSONObject();
            message.put("role", "user");
            message.put("content", text);
            messages.put(message);
            body.put("messages", messages);
            body.put("stream", false);
            asyncAbsolute("POST", "http://127.0.0.1:4097/v1/chat/completions", body.toString(), cb);
        } catch (Exception e) {
            main.post(() -> cb.failure(e.toString()));
        }
    }

    public void passthroughHistory(String sessionId, Callback cb) {
        asyncAbsolute(
                "GET",
                "http://127.0.0.1:4097/history?sessionID=" + enc(sessionId),
                null,
                cb);
    }

    public void appendPassthroughHistory(String sessionId, String role, String content, Callback cb) {
        try {
            JSONObject body = new JSONObject();
            body.put("sessionID", sessionId);
            JSONArray messages = new JSONArray();
            JSONObject message = new JSONObject();
            message.put("role", role);
            message.put("content", content);
            messages.put(message);
            body.put("messages", messages);
            asyncAbsolute("POST", "http://127.0.0.1:4097/history", body.toString(), cb);
        } catch (Exception e) {
            main.post(() -> cb.failure(e.toString()));
        }
    }

    public void abort(String sessionId, String directory, Callback cb) {
        async("POST", "/session/" + enc(sessionId) + "/abort?" + routing(directory), null, cb);
    }

    public void diff(String sessionId, String directory, Callback cb) {
        async("GET", "/session/" + enc(sessionId) + "/diff?" + routing(directory), null, cb);
    }

    public void listFiles(String directory, String path, Callback cb) {
        async("GET", "/file?" + routing(directory) + "&path=" + enc(path), null, cb);
    }

    public void readFile(String directory, String path, Callback cb) {
        async("GET", "/file/content?" + routing(directory) + "&path=" + enc(path), null, cb);
    }

    public void workspaceList(String root, String path, Callback cb) {
        asyncAbsolute(
                "GET",
                "http://127.0.0.1:4097/fs/list?root=" + enc(root) + "&path=" + enc(path),
                null,
                cb);
    }

    public void workspaceRead(String root, String path, Callback cb) {
        asyncAbsolute(
                "GET",
                "http://127.0.0.1:4097/fs/read?root=" + enc(root) + "&path=" + enc(path),
                null,
                cb);
    }

    public void workspaceSearch(String root, String query, Callback cb) {
        asyncAbsolute(
                "GET",
                "http://127.0.0.1:4097/fs/search?root=" + enc(root) + "&query=" + enc(query) + "&limit=100",
                null,
                cb);
    }

    public void workspaceWrite(String root, String path, String content, Callback cb) {
        try {
            JSONObject body = new JSONObject();
            body.put("root", root);
            body.put("path", path);
            body.put("content", content == null ? "" : content);
            asyncAbsolute("POST", "http://127.0.0.1:4097/fs/write", body.toString(), cb);
        } catch (Exception e) {
            main.post(() -> cb.failure(e.toString()));
        }
    }

    public void workspaceMkdir(String root, String path, Callback cb) {
        try {
            JSONObject body = new JSONObject();
            body.put("root", root);
            body.put("path", path);
            body.put("parents", false);
            asyncAbsolute("POST", "http://127.0.0.1:4097/fs/mkdir", body.toString(), cb);
        } catch (Exception e) {
            main.post(() -> cb.failure(e.toString()));
        }
    }

    public void runCommand(String root, String cwd, String command, int timeoutSeconds, Callback cb) {
        try {
            JSONObject body = new JSONObject();
            body.put("root", root);
            body.put("cwd", cwd == null || cwd.trim().isEmpty() ? "." : cwd.trim());
            body.put("command", command == null ? "" : command);
            body.put("timeoutSeconds", timeoutSeconds);
            asyncAbsolute("POST", "http://127.0.0.1:4097/exec", body.toString(), cb);
        } catch (Exception e) {
            main.post(() -> cb.failure(e.toString()));
        }
    }

    public void listPermissions(String directory, Callback cb) {
        async("GET", "/permission?" + routing(directory), null, cb);
    }

    public void replyPermission(String requestId, String directory, String reply, String message, Callback cb) {
        try {
            JSONObject body = new JSONObject();
            body.put("reply", reply);
            if (message != null && !message.trim().isEmpty()) body.put("message", message.trim());
            async("POST", "/permission/" + enc(requestId) + "/reply?" + routing(directory), body.toString(), cb);
        } catch (Exception e) {
            main.post(() -> cb.failure(e.toString()));
        }
    }

    public void listQuestions(String directory, Callback cb) {
        async("GET", "/question?" + routing(directory), null, cb);
    }

    public void replyQuestion(String requestId, String directory, JSONArray answers, Callback cb) {
        try {
            JSONObject body = new JSONObject();
            body.put("answers", answers);
            async("POST", "/question/" + enc(requestId) + "/reply?" + routing(directory), body.toString(), cb);
        } catch (Exception e) {
            main.post(() -> cb.failure(e.toString()));
        }
    }

    public void rejectQuestion(String requestId, String directory, Callback cb) {
        async("POST", "/question/" + enc(requestId) + "/reject?" + routing(directory), null, cb);
    }

    public void startEvents(String directory, EventListener listener) {
        stopEvents();
        eventLoop = true;
        pool.execute(() -> {
            String reason = "stream closed";
            try {
                URL url = new URL(baseUrl + "/event?" + routing(directory));
                HttpURLConnection c = (HttpURLConnection) url.openConnection();
                eventConnection = c;
                c.setRequestMethod("GET");
                c.setRequestProperty("Accept", "text/event-stream");
                c.setConnectTimeout(5000);
                c.setReadTimeout(0);
                int code = c.getResponseCode();
                if (code < 200 || code >= 300) {
                    reason = "event stream HTTP " + code + ": " + read(c.getErrorStream());
                } else {
                    BufferedReader reader = new BufferedReader(new InputStreamReader(c.getInputStream(), StandardCharsets.UTF_8));
                    String line;
                    while (eventLoop && (line = reader.readLine()) != null) {
                        if (line.startsWith("data:")) {
                            String payload = line.substring(5).trim();
                            main.post(() -> listener.event(payload));
                        }
                    }
                }
            } catch (Exception e) {
                reason = e.getMessage() == null ? e.toString() : e.getMessage();
            } finally {
                eventConnection = null;
                if (eventLoop) {
                    String finalReason = reason;
                    main.post(() -> listener.closed(finalReason));
                }
            }
        });
    }

    public void stopEvents() {
        eventLoop = false;
        HttpURLConnection c = eventConnection;
        if (c != null) c.disconnect();
        eventConnection = null;
    }

    public void shutdown() {
        stopEvents();
        pool.shutdownNow();
    }

    private void async(String method, String path, String body, Callback cb) {
        asyncAbsolute(method, baseUrl + path, body, cb);
    }

    private void asyncAbsolute(String method, String url, String body, Callback cb) {
        pool.execute(() -> {
            try {
                String result = requestAbsolute(method, url, body);
                main.post(() -> cb.success(result));
            } catch (Exception e) {
                String msg = e.getMessage() == null ? e.toString() : e.getMessage();
                main.post(() -> cb.failure(msg));
            }
        });
    }

    private String request(String method, String path, String body) throws Exception {
        return requestAbsolute(method, baseUrl + path, body);
    }

    private String requestAbsolute(String method, String url, String body) throws Exception {
        HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
        c.setRequestMethod(method);
        c.setRequestProperty("Accept", "application/json");
        c.setConnectTimeout(6000);
        c.setReadTimeout(120000);
        if (body != null) {
            c.setDoOutput(true);
            c.setRequestProperty("Content-Type", "application/json; charset=utf-8");
            byte[] data = body.getBytes(StandardCharsets.UTF_8);
            c.setFixedLengthStreamingMode(data.length);
            try (OutputStream out = c.getOutputStream()) {
                out.write(data);
            }
        }
        int code = c.getResponseCode();
        InputStream stream = code >= 200 && code < 300 ? c.getInputStream() : c.getErrorStream();
        String response = read(stream);
        c.disconnect();
        if (code < 200 || code >= 300) {
            throw new IllegalStateException("HTTP " + code + (response.isEmpty() ? "" : ": " + response));
        }
        return response;
    }

    private static String routing(String directory) {
        return "directory=" + enc(directory == null ? "" : directory);
    }

    private static String enc(String value) {
        try {
            return URLEncoder.encode(value == null ? "" : value, "UTF-8").replace("+", "%20");
        } catch (Exception e) {
            return "";
        }
    }

    private static String read(InputStream input) throws Exception {
        if (input == null) return "";
        try (InputStream in = input; ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[8192];
            int n;
            while ((n = in.read(buffer)) != -1) out.write(buffer, 0, n);
            return out.toString(StandardCharsets.UTF_8.name());
        }
    }
}
