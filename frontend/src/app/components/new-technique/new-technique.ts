import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { WebService } from '../../services/web-service';
import { AuthService } from '../../services/auth-service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-new-technique',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './new-technique.html',
  styleUrl: './new-technique.css'
})
export class NewTechnique implements OnInit {
  techniqueForm!: FormGroup;
  selectedFile: File | null = null;
  videoPreview: string | null = null;
  isSubmitting = false;
  backendError: string | null = null;

  allowedCategories = [
    { label: 'Guards', value: "Guard"},
    { label: 'Passing', value: 'Pass'},
    { label: 'Sweeps', value: 'Sweep'},
    { label: 'Takedowns', value: 'Takedown'},
    { label: 'Submissions', value: 'Submission'},
    { label: 'Escapes', value: 'Escape'},
    { label: 'Transitions', value: 'Transition'},
    { label: 'Drills', value: 'Drill'},
    { label: 'Pins', value: 'Pin'},
    { label: 'Rolls', value: 'Roll'}
  ];

  allowedDifficulties = ['Beginner', 'Intermediate', 'Advanced'];

  constructor(
    private fb: FormBuilder,
    private webService: WebService,
    public auth: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.techniqueForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(3)]],
      category: ['', [Validators.required]],
      difficulty: ['', [Validators.required]],
      description: ['', [Validators.required, Validators.minLength(10)]]
    });
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.selectedFile = file;
      this.videoPreview = URL.createObjectURL(file);
    }
  }

  cancel() {
    this.router.navigate(['/techniques']);
  }

  onSubmit(): void {
    if (this.techniqueForm.invalid || !this.selectedFile) {
      this.backendError = "Please fill all fields and select a video.";
      return;
    }

    this.isSubmitting = true;
    this.backendError = null;

    const data = {
      ...this.techniqueForm.value,
      videoFile: this.selectedFile
    };

    this.webService.postTechnique(data).subscribe({
      next: (res) => {
        this.isSubmitting = false;
        this.router.navigate(
          ['/techniques', res.id],
          {replaceUrl: true}
        );
      },
      error: (err) => {
        this.isSubmitting = false;
        this.backendError = err.error?.error || "An error occurred during upload.";
      }
    });
  }

  isInvalid(control: string): boolean {
    return this.techniqueForm.get(control)!.invalid && this.techniqueForm.get(control)!.touched;
  }
}