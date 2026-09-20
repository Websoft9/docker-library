package com.websoft9.demo;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {

    @GetMapping("/")
    public String index() {
        return "Spring Boot is running. Try GET /hello or /actuator/health";
    }

    @GetMapping("/hello")
    public Map<String, Object> hello() {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("message", "Hello from Spring Boot");
        body.put("time", Instant.now().toString());
        return body;
    }
}
