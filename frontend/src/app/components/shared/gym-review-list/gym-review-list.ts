import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../../services/auth-service';

@Component({
  selector: 'app-gym-review-list',
  imports: [CommonModule, FormsModule],
  templateUrl: './gym-review-list.html',
  styleUrl: './gym-review-list.css',
})
export class GymReviewList {
  /** Array of review objects to display */
  @Input() reviews: any[] = [];

  /** Section title for display above the list */
  @Input() title: string = "Reviews";

  /** Emits edited review data */
  @Output() onEdit = new EventEmitter<any>();

  /** Emits the review selected for deletion */
  @Output() onDelete = new EventEmitter<any>();

  /** Temporarily stores the review being edited */
  editingReview: any = null;

  /** Controls visibility of the edit modal */
  showEditModal = false;

  /** Stores review selected for deletion */
  deleteTarget: any = null;
  
  /** Authentication service used to check ownership/admin rights */
  constructor(public auth: AuthService) {}

  /**
   * Converts a numeric rating into an array for star display.
   * @param rating The numeric rating value
   */
  toStars(rating: Number) {
    return Array(Number(rating)).fill(0);
  }

  /**
   * Opens the edit modal and loads selected review into editing buffer.
   */
  startEdit(review: any) {
    this.editingReview = { ...review };
    this.showEditModal = true;
  }

  /** Cancels editing without saving changes */
  cancelEdit() {
    this.editingReview = null;
  }

  /**
   * Emits the edited review to the parent component.
   * Closes the edit modal.
   */
  saveEdit() {
    this.onEdit.emit(this.editingReview);
    this.showEditModal = false;
  }

  /**
   * Opens the delete confirmation UI.
   */
  startDelete(review: any) {
    this.deleteTarget = review;
  }

  /** Cancels deletion process */
  cancelDelete() {
    this.deleteTarget = null;
  }

  /**
   * Confirms deletion and emits the selected review.
   */
  confirmDelete() {
    this.onDelete.emit(this.deleteTarget);
    this.deleteTarget = null;
  }
}
