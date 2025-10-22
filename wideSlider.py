import cv2
import numpy as np
import os
import sys

def create_wideSlider_video(input_image_path, output_video_path, duration=10, fps=30):
    """
    Creates a 1080x1920 vertical video from a single image with zoom, pan, and fade transition.
    
    Animation sequence:
    1. Start zoomed in on the LEFT side
    2. Pan smoothly to the RIGHT side (while maintaining zoom)
    3. Fade directly to the full picture (no zoom animation, just crossfade)
    
    Args:
        input_image_path (str): Path to the input image
        output_video_path (str): Path for the output video (1080x1920)
        duration (int): Duration of the video in seconds (default: 10)
        fps (int): Frames per second (default: 30)
    """
    # Load the image
    img = cv2.imread(input_image_path)
    if img is None:
        raise ValueError(f"Could not load image from {input_image_path}")
    
    orig_h, orig_w = img.shape[:2]
    target_w, target_h = 1080, 1920  # 9:16 aspect ratio
    target_aspect = target_w / target_h  # 0.5625
    
    # Video settings
    total_frames = duration * fps
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (target_w, target_h))
    
    # Calculate safe zoom factor to ensure we can pan across the entire width
    crop_aspect = target_aspect
    max_zoom_for_width = orig_h / (orig_w / crop_aspect)
    base_zoom = min(2.0, max_zoom_for_width * 0.9)
    min_crop_h = target_h
    min_zoom_for_quality = min_crop_h / orig_h
    zoom_factor = max(base_zoom, min_zoom_for_quality)
    
    # Define timing
    pan_end_frame = int(total_frames * 0.6)  # Pan ends at 60% of video
    fade_duration_frames = int(fps * 1.0)    # 1 second fade duration
    fade_start_frame = pan_end_frame
    fade_end_frame = min(fade_start_frame + fade_duration_frames, total_frames)
    
    print(f"Original image: {orig_w}x{orig_h}")
    print(f"Output video: {target_w}x{target_h} (9:16)")
    print(f"Using zoom factor: {zoom_factor:.2f}x")
    print(f"Pan ends at frame: {pan_end_frame}")
    print(f"Fade from frame {fade_start_frame} to {fade_end_frame}")
    
    # Pre-calculate the final full image frame (without distortion)
    img_aspect = orig_w / orig_h
    if img_aspect >= target_aspect:
        # Image is wider than 9:16 - scale by width (letterbox top/bottom)
        scale = target_w / orig_w
        new_w = target_w
        new_h = int(orig_h * scale)
        final_frame = np.zeros((target_h, target_w, 3), dtype=np.uint8)
        y_offset = (target_h - new_h) // 2
        resized_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        final_frame[y_offset:y_offset+new_h, 0:new_w] = resized_img
    else:
        # Image is taller than 9:16 - scale by height (pillarbox left/right)
        scale = target_h / orig_h
        new_h = target_h
        new_w = int(orig_w * scale)
        final_frame = np.zeros((target_h, target_w, 3), dtype=np.uint8)
        x_offset = (target_w - new_w) // 2
        resized_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        final_frame[0:new_h, x_offset:x_offset+new_w] = resized_img
    
    # Generate frames
    for frame_num in range(total_frames):
        if frame_num < fade_start_frame:
            # Zoomed-in phase: pan from left to right
            if frame_num <= int(total_frames * 0.6):
                # Calculate pan position (left to right)
                pan_progress = frame_num / pan_end_frame if pan_end_frame > 0 else 1.0
                # Smooth interpolation for pan
                pan_smooth = pan_progress * pan_progress * (3 - 2 * pan_progress)
                cx_val = orig_w * 0.25 + (orig_w * 0.5) * pan_smooth  # 0.25 to 0.75
                cy_val = orig_h / 2
                
                # Crop and resize maintaining aspect ratio
                crop_h = int(orig_h / zoom_factor)
                crop_w = int(crop_h * crop_aspect)
                crop_w = min(crop_w, orig_w)
                crop_h = min(crop_h, orig_h)
                
                left = int(cx_val - crop_w / 2)
                right = left + crop_w
                top = int(cy_val - crop_h / 2)
                bottom = top + crop_h
                
                # Handle boundaries
                if left < 0:
                    left = 0
                    right = crop_w
                if right > orig_w:
                    right = orig_w
                    left = orig_w - crop_w
                if top < 0:
                    top = 0
                    bottom = crop_h
                if bottom > orig_h:
                    bottom = orig_h
                    top = orig_h - crop_h
                
                cropped = img[top:bottom, left:right]
                frame = cv2.resize(cropped, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
            else:
                # Hold at right position
                cx_val = orig_w * 0.75
                cy_val = orig_h / 2
                
                crop_h = int(orig_h / zoom_factor)
                crop_w = int(crop_h * crop_aspect)
                crop_w = min(crop_w, orig_w)
                crop_h = min(crop_h, orig_h)
                
                left = int(cx_val - crop_w / 2)
                right = left + crop_w
                top = int(cy_val - crop_h / 2)
                bottom = top + crop_h
                
                if left < 0:
                    left = 0
                    right = crop_w
                if right > orig_w:
                    right = orig_w
                    left = orig_w - crop_w
                if top < 0:
                    top = 0
                    bottom = crop_h
                if bottom > orig_h:
                    bottom = orig_h
                    top = orig_h - crop_h
                
                cropped = img[top:bottom, left:right]
                frame = cv2.resize(cropped, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
        
        elif frame_num >= fade_end_frame:
            # After fade: show final full image
            frame = final_frame.copy()
        
        else:
            # Fade transition phase
            fade_progress = (frame_num - fade_start_frame) / (fade_end_frame - fade_start_frame)
            
            # Get the zoomed-in frame at right position
            cx_val = orig_w * 0.75
            cy_val = orig_h / 2
            
            crop_h = int(orig_h / zoom_factor)
            crop_w = int(crop_h * crop_aspect)
            crop_w = min(crop_w, orig_w)
            crop_h = min(crop_h, orig_h)
            
            left = int(cx_val - crop_w / 2)
            right = left + crop_w
            top = int(cy_val - crop_h / 2)
            bottom = top + crop_h
            
            if left < 0:
                left = 0
                right = crop_w
            if right > orig_w:
                right = orig_w
                left = orig_w - crop_w
            if top < 0:
                top = 0
                bottom = crop_h
            if bottom > orig_h:
                bottom = orig_h
                top = orig_h - crop_h
            
            cropped = img[top:bottom, left:right]
            zoomed_frame = cv2.resize(cropped, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
            
            # Crossfade between zoomed frame and final full frame
            frame = cv2.addWeighted(zoomed_frame, 1.0 - fade_progress, final_frame, fade_progress, 0)
        
        # Write frame to video
        out.write(frame)
    
    # Release resources
    out.release()
    print(f"✅ Vertical video saved to: {output_video_path}")

def main():
    # Create input and output folders if they don't exist
    input_folder = "input"
    output_folder = "output"
    
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    
    # Get all image files from input folder
    supported_extensions = ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')
    image_files = [f for f in os.listdir(input_folder) 
                   if f.endswith(supported_extensions)]
    
    if not image_files:
        print("❌ No input images found in 'input' folder!")
        print("Please add JPG or PNG files to the 'input' folder and run again.")
        return
    
    print(f"📁 Found {len(image_files)} image(s) to process:")
    for img_file in image_files:
        print(f"  - {img_file}")
    
    # Process each image
    for img_file in image_files:
        input_path = os.path.join(input_folder, img_file)
        # Create output filename (replace extension with .mp4)
        output_filename = os.path.splitext(img_file)[0] + ".mp4"
        output_path = os.path.join(output_folder, output_filename)
        
        print(f"\n🎬 Processing: {img_file}")
        try:
            create_wideSlider_video(input_path, output_path)
        except Exception as e:
            print(f"💥 Error processing {img_file}: {str(e)}")
            continue
    
    print(f"\n🎉 All done! Videos saved to '{output_folder}' folder.")

if __name__ == "__main__":
    main()