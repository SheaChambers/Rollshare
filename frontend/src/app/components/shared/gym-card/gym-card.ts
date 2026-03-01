import { Component, Input } from '@angular/core';
import { WebService } from '../../../services/web-service';
import { AuthService } from '../../../services/auth-service';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-gym-card',
  imports: [CommonModule, FormsModule],
  templateUrl: './gym-card.html',
  styleUrl: './gym-card.css',
})
export class GymCard {

  /** Raw list of gyms returned from backend pagination */
  @Input() gym: any;

  /** Fallback thumbnail when a gym has no uploaded photos */
  fallbackThumb = "assets/images/no-image.jpg";

  constructor(private router: Router) {}

  /** Navigates to the selected gym's detail page */
  viewGym() {
    this.router.navigate(['/gyms', this.gym._id]);
  }

  /**
   * Determines the thumbnail URL for a gym, falling
   * back to a default image where necessary.
   */
  getGymThumbnail(): string {
    if (this.gym?.photos?.length > 0) {
      const first = this.gym.photos[0];
      return first.startsWith("http")
        ? first
        : "http://localhost:5001/static/" + first;
    }
    return this.fallbackThumb;
  }

  /**
   * Calculates the average rating for a gym from its reviews.
   * @returns The average rating (0–5)
   */
  averageRating(): number {
    if (!this.gym?.reviews || !this.gym?.reviews?.length) return 0;
    const total = this.gym.reviews.reduce(
      (sum: number, r: any) => sum + Number(r.rating),
      0
    );
    return total / this.gym.reviews.length;
  }

  /**
   * Produces an array for star rendering based on average rating.
   * @returns An array of the length equal to rounded average rating
   */
  getStars() {
    const avg = this.averageRating();
    return Array(Math.round(avg)).fill(0);
  }
}
