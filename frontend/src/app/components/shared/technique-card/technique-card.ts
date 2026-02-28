import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { WebService } from '../../../services/web-service';
import { AuthService } from '../../../services/auth-service';

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
  constructor(
    private router: Router,
    private webService: WebService,
    public auth: AuthService
  ) {}

  /**
   * Navigates to the technique detail page for the selected technique.
   */
  viewTechnique() {
    this.router.navigate(['/techniques', this.technique._id]);
  }

  toggleLike(event: Event) {
    event.stopPropagation();

    if (!this.auth.isLoggedIn()) {
      alert("Please log in to like techniques");
      return;
    }

    this.webService.toggleLike(this.technique._id)
      .subscribe((res: any) => {
        if (!this.technique.likes) {
          this.technique.likes = [];
        }

        const username = this.auth.getUsername();

        if (res.liked) {
          this.technique.likes.push(username);
        } else {
          this.technique.likes = 
            this.technique.likes.filter((u: string) => u !== username);
        }
      });
  }

  toggleSave(event: Event) {
    event.stopPropagation();

    if (!this.auth.isLoggedIn()) {
      alert("Please log in to save techniques!");
      return;
    }

    if (this.technique.isSaved) {
      this.webService.unsaveTechnique(this.technique._id)
        .subscribe(() =>
          this.technique.isSaved = false);
    } else {
      this.webService.saveTechnique(this.technique._id)
        .subscribe(() => 
          this.technique.isSaved = true);
    }
  }
}
