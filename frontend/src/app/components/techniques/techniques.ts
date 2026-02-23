import { Component } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth-service';

/**
 * The Techniques component provides the main search interface for techniques.
 * Users can search by keyword, navigate between categories, or create new techniques
 * (if logged in). It loads results dynamically as the user types or modifies filters.
 */
@Component({
  selector: 'app-techniques',
  imports: [RouterModule, CommonModule, FormsModule],
  templateUrl: './techniques.html',
  styleUrl: './techniques.css',
})
export class Techniques {

  /** List of technique categories displayed on the page */
  categories = [
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

  /** User search input tied to query params */
  searchQuery: string = "";

  /** Results returned from backend search */
  technique_list: any;

  /**
   * Injects services for data retrieval, navigation, and authentication.
   */
  constructor(
    private router: Router,
    public auth: AuthService
  ) {}

  /** Redirects user to the technique creation page */
  addTechnique() {
    this.router.navigate(['/techniques/new']);
  }

  /**
   * Navigates the user to the category-specific techniques view.
   * @param category The category name
   */
  goToCategory(category: string) {
    this.router.navigate(['/techniques/category', category]);
  }
}
