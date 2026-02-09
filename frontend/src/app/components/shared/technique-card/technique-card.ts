import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

/**
 * The TechniqueCard component displays a small preview card of a technique,
 * including its thumbnail, name, and metadata.  
 * Clicking the card navigates the user to the full technique detail page.
 */
@Component({
  selector: 'app-technique-card',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './technique-card.html',
  styleUrl: './technique-card.css',
})
export class TechniqueCard {

  /** Technique object containing title, image, metadata, etc. */
  @Input() technique: any;

  /** Allows for parent components to change the button text */
  @Input() buttonText: string = 'View Technique';

  /**
   * Injects Angular router to enable navigation to technique detail page.
   */
  constructor(private router: Router) {}

  /**
   * Navigates to the technique detail page for the selected technique.
   */
  viewTechnique() {
    this.router.navigate(['/techniques', this.technique._id]);
  }
}
