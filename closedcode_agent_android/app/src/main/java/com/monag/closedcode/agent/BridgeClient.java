package com.monag.closedcode.agent;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

final class BridgeClient {
    private static final int CONNECT_TIMEOUT_MS = 3000;
    private static final int READ_TIMEOUT_MS = 310000;

    private BridgeClient() {}

    static JSONObject ping(String token, int port, String requestId, String sessionId) throws Exception {
        JSONObject request = baseRequest(token, requestId, sessionId);
        request.put("op", "system.ping");
        request.put("params", new JSONObject());
        return send(port, request, 5000);
    }

    static JSONObject submitMission(
            String token,
            int port,
            String requestId,
            String sessionId,
            String prompt,
            String provider,
            String model) throws Exception {
        JSONObject params = new JSONObject();
        params.put("prompt", prompt);
        params.put("provider", provider);
        params.put("model", model);

        JSONObject request = baseRequest(token, requestId, sessionId);
        request.put("op", "mission.submit");
        request.put("params", params);
        return send(port, request, READ_TIMEOUT_MS);
    }

    private static JSONObject baseRequest(
            String token,
            String requestId,
            String sessionId) throws Exception {
        JSONObject request = new JSONObject();
        request.put("protocol", "closedcode.bridge.v1");
        request.put("token", token);
        request.put("request_id", requestId);
        request.put("session_id", sessionId);
        return request;
    }

    private static JSONObject send(int port, JSONObject request, int timeoutMs) throws Exception {
        try (Socket socket = new Socket()) {
            socket.connect(new InetSocketAddress("127.0.0.1", port), CONNECT_TIMEOUT_MS);
            socket.setSoTimeout(timeoutMs);

            BufferedWriter writer = new BufferedWriter(
                    new OutputStreamWriter(socket.getOutputStream(), StandardCharsets.UTF_8));
            writer.write(request.toString());
            writer.write("\n");
            writer.flush();

            BufferedReader reader = new BufferedReader(
                    new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8));
            String line = reader.readLine();
            if (line == null) {
                throw new IllegalStateException("ClosedCode bridge closed without a response");
            }

            JSONObject response = new JSONObject(line);
            if (!response.optBoolean("ok", false)) {
                throw new IllegalStateException(
                        "ClosedCode bridge rejected request: " + response.optString("error", "unknown_error"));
            }
            return response;
        }
    }
}
