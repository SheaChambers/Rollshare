import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { WebService } from '../../services/web-service';
import { AuthService } from '../../services/auth-service';
import { ReviewList } from '../shared/review-list/review-list';
import { ReviewForm } from '../shared/review-form/review-form';

@Component({
  selector: 'app-technique',
  imports: [RouterModule, CommonModule, ReviewList, ReviewForm],
  templateUrl: './technique.html',
  styleUrl: './technique.css',
})
export class Technique implements OnInit {
  technique: any;
  reviews: any[] = [];
  reviewForm: any;
  showReviews = false;
  activeTab: string = 'reviews';
  videoUrl?: SafeResourceUrl;
  thumbnailUrl?: string;
  isLoading: boolean = true;

  constructor(
    private route: ActivatedRoute,
    private sanitiser: DomSanitizer,
    private webService: WebService,
    public auth: AuthService
  ) {}

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadTechniqueData(id);
    }
  }

  loadTechniqueData(id: string) {
    this.isLoading = true;

    this.webService.getTechnique(id).subscribe(res => {
      this.technique = res;
      if (res.video_blob_url) {
        this.videoUrl = this.sanitiser.bypassSecurityTrustResourceUrl(
          res.video_blob_url
        );
      }
      this.thumbnailUrl = res.thumbnail_blob_url || null;
      this.isLoading = false;
    });

    this.webService.getReviews(id).subscribe(res => {
      this.reviews = res;
    });
  }

  toggleReviews() {
    this.showReviews = !this.showReviews;
  }

  /**
   * Reloads the list of reviews for this technique.
   */
  refreshReviews() {
    if (!this.technique || !this.technique?._id) return;

    this.webService.getReviews(this.technique._id)
      .subscribe(response => this.reviews = response);
  }

  /**
   * Emits an update request for a review and refreshes the list.
   */
  onEditReview(updatedReview: any) {
    this.webService.editReview(this.technique._id, updatedReview._id, updatedReview)
      .subscribe(() => this.refreshReviews());
  }

  /**
   * Deletes a review and refreshes the review list.
   */
  onDeleteReview(review: any) {
    this.webService.deleteReview(this.technique._id, review._id)
      .subscribe(() => this.refreshReviews());
  }

  saveToLibrary() {
    if (!this.auth.isLoggedIn) {
      alert("Please log in to save techniques!");
      return;
    }

    this.webService.saveTechnique(this.technique._id)
      .subscribe({next: () => {
        this.technique.isSaved = true;
        alert('Technique saved to your library!');
      },
      error: (err) => console.error("Error saving technique", err)
    });
  }

  unsaveFromLibrary() {
    this.webService.unsaveTechnique(this.technique._id).subscribe({
      next: () => {
        this.technique.isSaved = false;
        alert("Removed from library");
      }
    });
  }

  uploadForAI() {
    // Placeholder for AI video analysis upload
    console.log('Redirecting to AI upload service...');
  }
}