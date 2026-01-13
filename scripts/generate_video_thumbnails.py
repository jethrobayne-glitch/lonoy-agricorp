"""
Script to generate thumbnails for existing videos that don't have them.
Run this script to create thumbnails for videos uploaded before thumbnail generation was implemented.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from web import create_app
from web.models import db, StudyVideo
import cv2
from PIL import Image

STUDY_VIDEO_FOLDER = 'web/static/uploads/study_videos'
STUDY_THUMBNAIL_FOLDER = 'web/static/uploads/study_videos/thumbnails'

def generate_video_thumbnail(video_path, thumbnail_path, timestamp=1.0):
    """
    Generate a thumbnail from a video file at a specific timestamp.
    """
    try:
        # Open the video file
        video = cv2.VideoCapture(video_path)
        
        if not video.isOpened():
            print(f"  ❌ Could not open video: {video_path}")
            return False
        
        # Get video properties
        fps = video.get(cv2.CAP_PROP_FPS)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate frame number to capture
        frame_number = min(int(fps * timestamp), total_frames - 1)
        
        # Set video position to the desired frame
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        
        # Read the frame
        success, frame = video.read()
        
        if success:
            # Resize thumbnail to a reasonable size (maintaining aspect ratio)
            height, width = frame.shape[:2]
            max_width = 400
            if width > max_width:
                ratio = max_width / width
                new_width = max_width
                new_height = int(height * ratio)
                frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # Convert BGR to RGB (OpenCV uses BGR by default)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image and save as JPEG
            img = Image.fromarray(frame)
            img.save(thumbnail_path, 'JPEG', quality=85, optimize=True)
            
            video.release()
            print(f"  ✅ Thumbnail generated: {os.path.basename(thumbnail_path)}")
            return True
        
        video.release()
        print(f"  ❌ Could not read frame from video")
        return False
        
    except Exception as e:
        print(f"  ❌ Error generating thumbnail: {str(e)}")
        return False

def main():
    app = create_app()
    
    with app.app_context():
        # Ensure thumbnail directory exists
        os.makedirs(STUDY_THUMBNAIL_FOLDER, exist_ok=True)
        
        # Get all videos without thumbnails
        videos = StudyVideo.query.filter(
            (StudyVideo.thumbnail_path == None) | (StudyVideo.thumbnail_path == '')
        ).all()
        
        if not videos:
            print("✅ All videos already have thumbnails!")
            return
        
        print(f"📹 Found {len(videos)} videos without thumbnails")
        print("🔄 Generating thumbnails...\n")
        
        success_count = 0
        fail_count = 0
        
        for video in videos:
            print(f"Processing: {video.title}")
            
            # Check if video file exists
            if not os.path.exists(video.file_path):
                print(f"  ⚠️  Video file not found: {video.file_path}")
                fail_count += 1
                continue
            
            # Generate thumbnail filename
            thumbnail_filename = f"thumb_{video.filename.rsplit('.', 1)[0]}.jpg"
            thumbnail_path = os.path.join(STUDY_THUMBNAIL_FOLDER, thumbnail_filename)
            
            # Generate thumbnail
            if generate_video_thumbnail(video.file_path, thumbnail_path):
                # Update database
                video.thumbnail_path = f"/static/uploads/study_videos/thumbnails/{thumbnail_filename}"
                success_count += 1
            else:
                fail_count += 1
        
        # Commit changes
        db.session.commit()
        
        print(f"\n{'='*50}")
        print(f"✅ Successfully generated: {success_count} thumbnails")
        if fail_count > 0:
            print(f"❌ Failed: {fail_count} thumbnails")
        print(f"{'='*50}")

if __name__ == '__main__':
    main()
