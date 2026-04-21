# Bitmap to SVG Vectorizer Design

This project is a small, testable Python CLI for converting simple bitmap images
into SVG paths. It is optimized for high-contrast logos, line art, icons, and
flat color illustrations rather than photographic vectorization.

## Pipeline

Binary mode reads an image, converts it to grayscale, denoises it, thresholds it
with either Otsu or a fixed value, cleans the mask with morphology, extracts
contours, simplifies them, and writes black filled SVG paths.

Color mode converts BGR input to RGB, quantizes colors with K-Means, extracts a
mask per representative color, traces each mask independently, and writes one
filled SVG path per detected color region.

## Coordinate System

OpenCV contours are traced in image coordinates. When `--max-size` is used, the
image is resized only for processing; generated points are scaled back to the
original image dimensions so the SVG `width`, `height`, and `viewBox` match the
source image.

## Holes and Fill Rules

Contour holes are preserved by using `cv2.RETR_CCOMP` and serializing outer and
inner contours into the same SVG path with `fill-rule="evenodd"`.

## Limits

The tool intentionally favors clear output and predictable behavior over
advanced vector-art reconstruction. Complex photos, gradients, shadows, and
textured images should be simplified before conversion or processed with color
mode and a small color count.

