package com.example.lab1;

import java.io.File;
import java.net.URL;
import java.util.Arrays;
import java.util.Random;
import java.util.ResourceBundle;

import javafx.fxml.FXML;
import javafx.scene.control.Alert;
import javafx.scene.control.Button;
import javafx.scene.control.ButtonType;
import javafx.scene.control.ScrollBar;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;

import javafx.stage.FileChooser;
import javafx.stage.Stage;
import javafx.scene.image.PixelReader;
import javafx.scene.image.WritableImage;

public class HelloController {

    @FXML
    private Button buttonLoad;

    @FXML
    private ImageView imageFixed;

    @FXML
    private ImageView imageOriginal;

    @FXML
    private ScrollBar scrollBar;

    private Image currentImage;

    private Image noisyImageView;

    @FXML
    public void initialize() {
        scrollBar.setMin(0);
        scrollBar.setMax(300);
        scrollBar.setValue(0);

        scrollBar.valueProperty().addListener((observable, oldValue, newValue) -> {
            if (currentImage != null) {
                addNoiseToImage(currentImage, imageFixed, (int) newValue.doubleValue());
            }
        });
    }

    @FXML
    public void loadImage() {
        Stage primaryStage = (Stage) buttonLoad.getScene().getWindow();
        FileChooser fileChooser = new FileChooser();
        fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("Image Files", "*.png", "*.jpg", "*.jpeg"));

        File selectedFile = fileChooser.showOpenDialog(primaryStage);

        if (selectedFile != null) {
            currentImage = new Image(selectedFile.toURI().toString());
            imageOriginal.setImage(currentImage);
            addNoiseToImage(currentImage, imageFixed, (int) scrollBar.getValue());
        }
    }

    @FXML
    public void Exit() {
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle("Хотите выйти?");
        ButtonType exit = new ButtonType("Выйти");
        ButtonType cont = new ButtonType("Продолжить");
        alert.getButtonTypes().setAll(exit, cont);
        alert.show();

        alert.setOnHidden(event -> {
            if (alert.getResult() == exit)
                System.exit(0);
        });
    }

    public void addNoiseToImage(Image imageOriginal, ImageView imageFixed, int value) {
        int width = (int) imageOriginal.getWidth();
        int height = (int) imageOriginal.getHeight();

        WritableImage noisyImage = new WritableImage(width, height);
        PixelReader pixelReader = imageOriginal.getPixelReader();

        Random random = new Random();

        for (int x = 0; x < width; x++) {
            for (int y = 0; y < height; y++) {
                int argb = pixelReader.getArgb(x, y);
                int r = (argb >> 16) & 0xFF;
                int g = (argb >> 8) & 0xFF;
                int b = argb & 0xFF;

                r = clamp(r + random.nextInt(value) - value / 2, 0, 255);
                g = clamp(g + random.nextInt(value) - value / 2, 0, 255);
                b = clamp(b + random.nextInt(value) - value / 2, 0, 255);

                int noisyArgb = (argb & 0xFF000000) | (r << 16) | (g << 8) | b;
                noisyImage.getPixelWriter().setArgb(x, y, noisyArgb);
            }
        }
        imageFixed.setImage(noisyImage);
        noisyImageView = noisyImage;
    }

    public void recover() {
        int width = (int) noisyImageView.getWidth();
        int height = (int) noisyImageView.getHeight();

        WritableImage recoverImage = new WritableImage(width, height);
        PixelReader pixelReader = noisyImageView.getPixelReader();

        for (int i = 0; i < width; i++) {
            for (int j = 0; j < height; j++) {
                int[] massRed = new int[9];
                int[] massGreen = new int[9];
                int[] massBlue = new int[9];
                int buf = 0;

                for (int x = Math.max(0, i - 1); x <= Math.min(width - 1, i + 1); x++) {
                    for (int y = Math.max(0, j - 1); y <= Math.min(height - 1, j + 1); y++) {
                        int argb = pixelReader.getArgb(x, y);

                        massRed[buf] = (argb >> 16) & 0xFF;
                        massGreen[buf] = (argb >> 8) & 0xFF;
                        massBlue[buf] = argb & 0xFF;
                        buf++;
                    }
                }

                while (buf < 9) {
                    massRed[buf] = 0;
                    massGreen[buf] = 0;
                    massBlue[buf] = 0;
                    buf++;
                }

                massRed = Arrays.stream(massRed).sorted().toArray();
                massGreen = Arrays.stream(massGreen).sorted().toArray();
                massBlue = Arrays.stream(massBlue).sorted().toArray();

                int recoverArgb = (0xFF << 24) | (massRed[4] << 16) | (massGreen[4] << 8) | massBlue[4];
                recoverImage.getPixelWriter().setArgb(i, j, recoverArgb);
            }
        }

        noisyImageView = recoverImage;
        imageFixed.setImage(noisyImageView);
    }


    private int clamp(int value, int min, int max) {
        return Math.max(min, Math.min(max, value));
    }
}