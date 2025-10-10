package com.example;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Lob;
import jakarta.persistence.Table;
import java.util.UUID;

@Entity
@Table(name = "images")
public class Image {

    @Id
    public UUID id;

    @Lob
    @Column(name = "image_data", nullable = false)
    public byte[] imageData;

    @Column(nullable = false)
    public String nickname;

    @Column(name = "mime_type", nullable = false)
    public String mimeType;
}
