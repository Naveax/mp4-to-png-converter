import cv2
import os
import sys
import time
from tkinter import Tk, Button, Label, filedialog, StringVar, Entry, Frame, messagebox
from tkinter.ttk import Progressbar
import threading

class Mp4ToPngConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("MP4 to PNG Converter")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Input file section
        input_frame = Frame(self.root)
        input_frame.pack(fill="x", padx=20, pady=20)
        
        Label(input_frame, text="MP4 File:").grid(row=0, column=0, sticky="w")
        
        self.file_path = StringVar()
        Entry(input_frame, textvariable=self.file_path, width=50).grid(row=0, column=1, padx=5)
        
        Button(input_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5)
        
        # Output directory section
        output_frame = Frame(self.root)
        output_frame.pack(fill="x", padx=20, pady=10)
        
        Label(output_frame, text="Output Directory:").grid(row=0, column=0, sticky="w")
        
        self.output_path = StringVar()
        self.output_path.set(os.path.join(os.getcwd(), "output"))
        Entry(output_frame, textvariable=self.output_path, width=50).grid(row=0, column=1, padx=5)
        
        Button(output_frame, text="Browse", command=self.browse_output_dir).grid(row=0, column=2, padx=5)
        
        # Progress section
        progress_frame = Frame(self.root)
        progress_frame.pack(fill="x", padx=20, pady=20)
        
        self.status_label = Label(progress_frame, text="Ready")
        self.status_label.pack()
        
        self.progress_bar = Progressbar(progress_frame, orient="horizontal", length=550, mode="determinate")
        self.progress_bar.pack(pady=10)
        
        self.frame_count_label = Label(progress_frame, text="")
        self.frame_count_label.pack()
        
        # Control buttons
        button_frame = Frame(self.root)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        self.convert_button = Button(button_frame, text="Start Conversion", command=self.start_conversion, height=2, width=20)
        self.convert_button.pack(side="left", padx=10)
        
        self.cancel_button = Button(button_frame, text="Cancel", command=self.cancel_conversion, height=2, width=20, state="disabled")
        self.cancel_button.pack(side="right", padx=10)
        
        # Status variables
        self.is_running = False
        self.conversion_thread = None
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select MP4 File",
            filetypes=(("MP4 files", "*.mp4"), ("All files", "*.*"))
        )
        if file_path:
            self.file_path.set(file_path)
    
    def browse_output_dir(self):
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.output_path.set(dir_path)
    
    def start_conversion(self):
        if not self.file_path.get().strip():
            messagebox.showerror("Error", "Please select an MP4 file")
            return
        
        output_dir = self.output_path.get().strip()
        if not output_dir:
            messagebox.showerror("Error", "Please specify an output directory")
            return
        
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create output directory: {str(e)}")
                return
        
        self.convert_button.config(state="disabled")
        self.cancel_button.config(state="normal")
        self.is_running = True
        
        self.conversion_thread = threading.Thread(target=self.convert_mp4_to_png)
        self.conversion_thread.start()
    
    def cancel_conversion(self):
        if self.is_running:
            self.is_running = False
            self.status_label.config(text="Cancelling...")
    
    def convert_mp4_to_png(self):
        try:
            video_path = self.file_path.get()
            output_dir = self.output_path.get()
            
            # Open video file
            video = cv2.VideoCapture(video_path)
            
            if not video.isOpened():
                self.update_status("Error: Could not open video file")
                return
            
            # Get video properties
            source_fps = video.get(cv2.CAP_PROP_FPS)
            frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / source_fps if source_fps > 0 else 0
            
            # Target frame rate (always 60 FPS)
            target_fps = 60.0
            
            # Calculate total frames at target FPS
            total_frames_at_target_fps = int((duration * target_fps) + 0.5)
            
            # Update UI with video info
            minutes = int(duration / 60)
            seconds = int(duration % 60)
            self.root.after(0, lambda: self.frame_count_label.config(
                text=f"Video: {source_fps:.2f} FPS → 60.00 FPS, {total_frames_at_target_fps} frames, Duration: {minutes}m {seconds}s"
            ))
            
            # Configure progress bar
            self.root.after(0, lambda: self.progress_bar.config(maximum=total_frames_at_target_fps))
            
            # Create output directory
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Process video frames
            count = 0
            frame_idx = 0
            start_time = time.time()
            prev_frame = None
            curr_frame = None
            
            while self.is_running and frame_idx < total_frames_at_target_fps:
                # Calculate the time position in the source video
                source_time = frame_idx / target_fps
                
                # Calculate the corresponding frame number in source
                source_frame_idx = source_time * source_fps
                
                # Get the floor and ceiling frame indices for interpolation
                source_frame_floor = int(source_frame_idx)
                source_frame_ceil = min(source_frame_floor + 1, frame_count - 1)
                
                # Calculate the interpolation factor
                alpha = source_frame_idx - source_frame_floor
                
                # Check if we need to read a new frame
                if prev_frame is None or source_frame_floor > count:
                    # Need to read frames until we reach the desired position
                    while count < source_frame_floor and self.is_running:
                        ret, frame = video.read()
                        if not ret:
                            break
                        count += 1
                        prev_frame = curr_frame
                        curr_frame = frame
                
                if curr_frame is None:
                    # Read at least one frame
                    ret, curr_frame = video.read()
                    if not ret:
                        break
                    count += 1
                
                if prev_frame is None:
                    prev_frame = curr_frame
                
                # Create the interpolated frame
                if alpha == 0 or prev_frame is None:
                    # Use the current frame directly
                    output_frame = curr_frame
                else:
                    # Use linear interpolation between frames
                    output_frame = cv2.addWeighted(prev_frame, 1.0 - alpha, curr_frame, alpha, 0)
                
                # Save the frame as PNG
                frame_path = os.path.join(output_dir, f"frame_{frame_idx:06d}.png")
                cv2.imwrite(frame_path, output_frame)
                
                # Update progress
                frame_idx += 1
                
                if frame_idx % 10 == 0:  # Update UI every 10 frames to avoid excessive updates
                    elapsed = time.time() - start_time
                    if elapsed > 0:
                        fps_processing = frame_idx / elapsed
                        eta = (total_frames_at_target_fps - frame_idx) / fps_processing if fps_processing > 0 else 0
                        eta_min = int(eta / 60)
                        eta_sec = int(eta % 60)
                        
                        self.root.after(0, lambda c=frame_idx, t=total_frames_at_target_fps, f=fps_processing, etam=eta_min, etas=eta_sec: self.update_progress(
                            c, t, f, etam, etas
                        ))
            
            # Close video file
            video.release()
            
            if self.is_running:  # If not canceled
                self.root.after(0, lambda: self.status_label.config(text="Conversion completed!"))
            else:
                self.root.after(0, lambda: self.status_label.config(text="Conversion canceled"))
                
        except Exception as e:
            self.root.after(0, lambda err=str(e): self.status_label.config(text=f"Error: {err}"))
        
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.convert_button.config(state="normal"))
            self.root.after(0, lambda: self.cancel_button.config(state="disabled"))
            self.root.after(0, lambda: self.progress_bar.config(value=0))
    
    def update_status(self, message):
        self.root.after(0, lambda msg=message: self.status_label.config(text=msg))
    
    def update_progress(self, current, total, fps, eta_min, eta_sec):
        self.progress_bar["value"] = current
        percentage = (current / total) * 100 if total > 0 else 0
        self.status_label.config(
            text=f"Converting: {current}/{total} frames ({percentage:.1f}%) - {fps:.1f} FPS - ETA: {eta_min}m {eta_sec}s"
        )

if __name__ == "__main__":
    root = Tk()
    app = Mp4ToPngConverter(root)
    root.mainloop() 