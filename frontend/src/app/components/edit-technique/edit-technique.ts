import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { WebService } from '../../services/web-service';
import { FormBuilder, Validators, ReactiveFormsModule, FormGroup } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth-service';

/**
 * The EditTechnique component allows administrators or the user
 * who created the technique to modify its details. It loads the
 * existing technique, validates user permissions, previews embedded
 * YouTube videos, and supports deletion of a technique.
 */
@Component({
  selector: 'app-edit-technique',
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './edit-technique.html',
  styleUrl: './edit-technique.css',
})
export class EditTechnique {

  /** Reactive form used to edit technique details */
  editForm!: FormGroup;

  /** ID of the technique being edited */
  techniqueId: any;

  /** Error message returned from backend operations */
  backendError: any;

  /** Whether the user is authorised to edit or delete the technique */
  authorised = false;

  /** Controls the visibility of the delete confirmation dialog */
  confirmDelete = false;

  /** Video file that has been selected */
  selectedFile: File | null = null;

  /** Allowed technique categories for the dropdown menu */
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

  /** Allowed difficulty levels for technique classification */
  allowedDifficulties = ['Beginner', 'Intermediate', 'Advanced'];

  /**
   * Injects required services for route access, API calls,
   * authentication, form creation, and navigation.
   */
  constructor(
    private formBuilder: FormBuilder,
    private route: ActivatedRoute,
    private webService: WebService,
    private auth: AuthService,
    private router: Router,
  ) {}

  /**
   * Initializes the edit form, loads the technique details,
   * verifies user permissions, and updates thumbnail preview
   * dynamically as the media URL changes.
   */
  ngOnInit() {
    this.editForm = this.formBuilder.group({
      name: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(50)]],
      category: ['', Validators.required],
      difficulty: ['', Validators.required],
      description: ['', [Validators.required, Validators.minLength(10), Validators.maxLength(500)]],
    });

    const id = this.route.snapshot.paramMap.get('id');
    this.techniqueId = id;

    this.webService.getTechnique(id!)
      .subscribe({ 
        next: (response: any) => {
          this.authorised = this.auth.isAdmin() || response.created_by === this.auth.getUsername();
          if (!this.authorised) return;

          this.editForm.patchValue(response);
        },

        error: () => {
          this.backendError = "Failed to load technique";
        }
    });
  }

  onFileSelected(event: any) {
    this.selectedFile = event.targer.files[0] as File;
  }

  /** Checks if a form control is invalid and touched */
  isInvalid(field: string) {
    const c = this.editForm.get(field);
    return c && c.invalid && c.touched;
  }

  /**
   * Sends the updated technique data to the backend.
   * Redirects to the techniques list on success.
   */
  updateTechnique() {
    const updateData = {
      ...this.editForm.value,
      videoFile: this.selectedFile
    };

    this.webService.editTechnique(this.techniqueId, this.editForm.value).subscribe({
      next: () => this.router.navigate(['/techniques/' + this.techniqueId]),
      error: (err: any) => {
        this.backendError = err.error?.error || "Update failed.";
      }
    });
  }

  /** Opens the delete confirmation dialog */
  openDeleteConfirm() {
    this.confirmDelete = true;
  }

  /**
   * Sends a delete request to the backend and redirects when complete.
   */
  deleteTechnique() {
    this.webService.deleteTechnique(this.techniqueId)
    .subscribe({
      next: () => this.router.navigate(['/techniques']),
      error: (err: any) => {
        this.backendError = err.error?.error || "Deletion failed.";
      }
    });
  }

  /** Navigates back to the techniques list */
  cancel() {
    this.router.navigate(['/techniques/' + this.techniqueId]);
  }
}
