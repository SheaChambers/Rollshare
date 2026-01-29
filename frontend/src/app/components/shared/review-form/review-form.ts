import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { WebService } from '../../../services/web-service';
import { AuthService } from '../../../services/auth-service';

/**
 * The ReviewForm component provides a form for users to submit a review
 * for either a technique or a gym. It supports dynamic routing based on
 * the parent type and emits an event when a review is successfully created.
 */
@Component({
  selector: 'app-review-form',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './review-form.html',
  styleUrl: './review-form.css',
})
export class ReviewForm {

  /** ID of the parent entity (technique or gym) being reviewed */
  @Input() parentId!: string;

  /** Specifies whether the review belongs to a technique or a gym */
  @Input() parentType!: 'technique' | 'gym';

  /** Emits when a new review is successfully submitted */
  @Output() reviewAdded = new EventEmitter<void>();

  /** Holds backend validation or server errors */
  backendError: string | null = null;

  /** Reactive review form object */
  reviewForm: any;

  /**
   * Injects services for form building, backend communication,
   * and checking user authentication.
   */
  constructor(
    private formBuilder: FormBuilder,
    private webService: WebService,
    public auth: AuthService
  ) {}

  /**
   * Builds the review form and applies validation rules for rating and comment.
   */
  ngOnInit() {
    this.reviewForm = this.formBuilder.group({
      rating: ['', Validators.required],
      comment: ['', [Validators.required, Validators.minLength(5)]],
    });
  }

  /**
   * Submits the review to the correct backend endpoint depending on the parent type.
   * Emits reviewAdded event on success.
   */
  submit() {
    if (this.reviewForm.invalid) return;
    this.backendError = null;

    let request$;

    if (this.parentType === 'technique') {
      request$ = this.webService.postReview(this.parentId, this.reviewForm.value);
    } else {
      request$ = this.webService.postGymReview(this.parentId, this.reviewForm.value);
    }

    request$.subscribe({
      next: () => {
        this.reviewForm.reset();
        this.reviewAdded.emit();
      },
      error: (err) => {
        this.backendError = err.error?.error || "Something went wrong.";
      }
    });
  }
}
