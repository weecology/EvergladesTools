import cv2
import numpy as np

def find_overlapping_images(image1, image2):
  """Finds overlapping images in two images.

  Args:
    image1: The first image.
    image2: The second image.

  Returns:
    A list of overlapping images.
  """

  # Convert the images to grayscale.
  gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
  gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

  # Find the keypoints and descriptors for each image.
  sift = cv2.SIFT_create()
  kp1, des1 = sift.detectAndCompute(gray1, None)
  kp2, des2 = sift.detectAndCompute(gray2, None)

  # Match the keypoints between the two images.
  bf = cv2.BFMatcher()
  matches = bf.knnMatch(des1, des2, k=2)

  # Filter out the bad matches.
  good_matches = []
  for m, n in matches:
    if m.distance < 0.75 * n.distance:
      good_matches.append(m)

  # Find the homography between the two images.
  if len(good_matches) > 10:
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    H, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

    # Warp the second image to the first image.
    warped_image = cv2.warpPerspective(image2, H, (image1.shape[1], image1.shape[0]))

    # Find the overlapping region.
    overlapping_region = cv2.bitwise_and(image1, warped_image)

    # Return the overlapping region.
    return overlapping_region
  else:
    return None
  
if __name__ == "__main__":
  # Load the images.
  image1 = cv2.imread("/Users/benweinstein/Downloads/DSC_2520.JPG")
  image2 = cv2.imread("/Users/benweinstein/Downloads/DSC_2521.JPG")

  # Find the overlapping images.
  overlapping_images = find_overlapping_images(image1, image2)

  # Display the overlapping images.
  cv2.imshow("Overlapping Images", overlapping_images)
  cv2.waitKey(0)
  cv2.destroyAllWindows()