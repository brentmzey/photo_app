package com.example;

import io.smallrye.reactive.messaging.annotations.Blocking;
import jakarta.enterprise.context.ApplicationScoped;
import org.eclipse.microprofile.reactive.messaging.Incoming;

@ApplicationScoped
public class NotificationConsumer {

    @Incoming("photo-app")
    @Blocking
    public void process(String imageId) {
        System.out.println("Received notification for uploaded image: " + imageId);
    }
}
