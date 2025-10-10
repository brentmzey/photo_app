package com.example;

import io.smallrye.mutiny.Uni;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.eclipse.microprofile.reactive.messaging.Channel;
import org.eclipse.microprofile.reactive.messaging.Emitter;
import org.jboss.resteasy.reactive.multipart.FileUpload;

import java.io.IOException;
import java.nio.file.Files;
import java.util.Base64;
import java.util.UUID;
import org.eclipse.microprofile.config.inject.ConfigProperty;

@Path("/")
@ApplicationScoped
public class ImageResource {

    @Inject
    ImageRepository imageRepository;

    @Inject
    ReactiveRedisClient reactiveRedisClient;

    @Inject
    @Channel("image-processing")
    Emitter<String> imageProcessingEmitter;

    @ConfigProperty(name = "quarkus.datasource.db-kind")
    String dbType;

    @POST
    @Consumes(MediaType.MULTIPART_FORM_DATA)
    @Produces(MediaType.TEXT_HTML)
    public Uni<Response> upload(FileUploadInput input) {
        String requestId = UUID.randomUUID().toString();
        try {
            byte[] imageData = Files.readAllBytes(input.imageData.uploadedFile());
            String mimeType = Files.probeContentType(input.imageData.uploadedFile());
            String image_data = Base64.getEncoder().encodeToString(imageData);

            ImageProcessingRequest request = new ImageProcessingRequest(requestId, input.nickname, image_data, mimeType);
            imageProcessingEmitter.send(request.toString());

            return Uni.createFrom().item(Response.accepted("<div class='success-message'>Request " + requestId + " received. Image '" + input.nickname + "' is being processed.</div>").build());
        } catch (IOException e) {
            e.printStackTrace();
            return Uni.createFrom().item(Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity("Image upload failed: " + e.getMessage()).build());
        }
    }

    @GET
    @Path("/images/{nickname}")
    @Produces(MediaType.APPLICATION_JSON)
    public Uni<Response> getImage(@PathParam("nickname") String nickname) {
        return reactiveRedisClient.get(nickname)
                .onItem().transformToUni(cachedImage -> {
                    if (cachedImage != null) {
                        String[] parts = cachedImage.toString().split("\\|");
                        String image_data = parts[0];
                        String mime_type = parts[1];
                        return Uni.createFrom().item(Response.ok(java.util.List.of(new ImageResponse(image_data, mime_type))).build());
                    }

                    return imageRepository.find("nickname", nickname).list()
                            .onItem().transformToUni(images -> {
                                if (images.isEmpty()) {
                                    return Uni.createFrom().item(Response.status(Response.Status.NOT_FOUND).build());
                                }
                                Image image = images.get(0);
                                String base64ImageData = Base64.getEncoder().encodeToString(image.imageData);
                                ImageResponse imageResponse = new ImageResponse(base64ImageData, image.mimeType);

                                return reactiveRedisClient.set(java.util.List.of(nickname, base64ImageData + "|" + image.mimeType))
                                        .onItem().transform(v -> Response.ok(java.util.List.of(imageResponse)).build());
                            });
                });
    }

    @GET
    @Path("/dbtype")
    @Produces(MediaType.APPLICATION_JSON)
    public Response dbtype() {
        return Response.ok(new DbTypeResponse(dbType)).build();
    }

    public static class FileUploadInput {
        @FormParam("nickname")
        public String nickname;

        @FormParam("image_data")
        public FileUpload imageData;
    }

    private static class ImageResponse {
        public String image_data;
        public String mime_type;

        public ImageResponse(String image_data, String mime_type) {
            this.image_data = image_data;
            this.mime_type = mime_type;
        }
    }

    public static class FileUploadInput {
        @FormParam("nickname")
        public String nickname;

        @FormParam("image_data")
        public FileUpload imageData;
    }

    private static class ImageProcessingRequest {
        public String request_id;
        public String nickname;
        public String image_data;
        public String mime_type;

        public ImageProcessingRequest(String request_id, String nickname, String image_data, String mime_type) {
            this.request_id = request_id;
            this.nickname = nickname;
            this.image_data = image_data;
            this.mime_type = mime_type;
        }

        @Override
        public String toString() {
            return "{\"request_id\":\"" + request_id + "\",\"nickname\":\"" + nickname + "\",\"image_data\":\"" + image_data + "\",\"mime_type\":\"" + mime_type + "\"}";
        }
    }

    private static class DbTypeResponse {
        public String db_type;

        public DbTypeResponse(String db_type) {
            this.db_type = db_type;
        }
    }
}
