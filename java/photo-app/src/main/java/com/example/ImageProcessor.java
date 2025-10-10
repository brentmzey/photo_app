package com.example;

import io.smallrye.reactive.messaging.annotations.Blocking;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import org.eclipse.microprofile.reactive.messaging.Channel;
import org.eclipse.microprofile.reactive.messaging.Emitter;
import org.eclipse.microprofile.reactive.messaging.Incoming;

import java.util.Base64;
import java.util.UUID;
import org.json.JSONObject;

@ApplicationScoped
public class ImageProcessor {

    @Inject
    ImageRepository imageRepository;

    @Inject
    @Channel("image-uploaded")
    Emitter<String> imageUploadedEmitter;

    @Incoming("image-processing")
    @Blocking
    @Transactional
    public void process(String message) {
        JSONObject json = new JSONObject(message);
        String requestId = json.getString("request_id");
        System.out.println("Processing request: " + requestId);

        Image image = new Image();
        image.id = UUID.randomUUID();
        image.nickname = json.getString("nickname");
        image.imageData = Base64.getDecoder().decode(json.getString("image_data"));
        image.mimeType = json.getString("mime_type");

        try {
            imageRepository.persist(image).await().indefinitely();
            imageUploadedEmitter.send(image.id.toString());
            System.out.println("Request " + requestId + " processed successfully.");
        } catch (Exception e) {
            System.err.println("Error processing request " + requestId + ": " + e.getMessage());
        }
    }
}
