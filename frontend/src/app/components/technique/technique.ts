import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { WebService } from '../../services/web-service';
import { AuthService } from '../../services/auth-service';
import { ReviewList } from '../shared/review-list/review-list';
import { ReviewForm } from '../shared/review-form/review-form';
import { BackButton } from '../shared/back-button/back-button';

@Component({
  selector: 'app-technique',
  imports: [RouterModule, CommonModule, ReviewList, ReviewForm, BackButton],
  templateUrl: './technique.html',
  styleUrl: './technique.css',
})
export class Technique implements OnInit {
  technique: any;
  reviews: any[] = [];
  reviewForm: any;
  showReviews = false;
  activeMainTab: string = 'details';
  activeContentTab: string = 'reviews';
  videoUrl?: SafeResourceUrl;
  thumbnailUrl?: string;
  isLoading: boolean = true;
  backendError: string | null = null;
  pollHandle: any;

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

      if (this.auth.isLoggedIn()) {
        this.checkIfSaved(id);
      }

      if (res.video_blob_url) {
        this.videoUrl = this.sanitiser.bypassSecurityTrustResourceUrl(
          res.video_blob_url
        );
      }

      if (res.analysis) {
        this.processAnalysisTimeline(res.analysis);
      }

      this.thumbnailUrl = res.thumbnail_blob_url || null;
      this.isLoading = false;
    });

    this.webService.getReviews(id).subscribe(res => {
      this.reviews = res;
    });
  }

  /**
   * Converts position key into readable label
   */
  formatPosition(key: string | number): string {
    return String(key).replace(/_/g, ' ');
  }

  /**
   * Sort distribution with highest percentage first
   */
  sortByPercentageDesc = (a: any, b: any): number => {
    return b.value - a.value;
  }

  /**
   * Prepares the AI segments for the CSS-driven timeline bar
   */
  processAnalysisTimeline(results: any) {

    if (!results || !Array.isArray(results.timeline)) {
      console.warn("Timeline missing or invalid:", results);
      return;
    }

    const segments = results.timeline;

    if (segments.length === 0) return;

    const first = segments[0];
    const last = segments[segments.length - 1];

    const totalDuration = last.end_s - first.start_s;

    results.timeline = segments.map((seg: any) => ({
      ...seg,
      durationPercentage:
        ((seg.end_s - seg.start_s) / totalDuration) * 100,
      label: seg.position,
      color: this.getPositionColor(seg.position)
    }));

    if (results.distribution) {
      results.sortedDistribution = Object.entries(results.distribution)
        .map(([key, value]) => ({ key, value }))
        .sort((a: any, b: any) => b.value - a.value);
    }
  }

  /**
   * Defines consistent colors for different BJJ positions
   */
  getPositionColor(label: string): string {
    const colors: { [key: string]: string } = {
      '5050_guard': '#49b5fe',
      'open_guard': '#5bffde',
      'closed_guard': '#2cfa82',
      'half_guard': '#fedb4f',

      'mount': '#fc4b37',
      'side_control': '#fc8931',
      'back': '#c942fe',
      
      'standing': '#ff87dd',
      'takedown': '#b6fe42',
      'turtle': '#066dfd'
    };
    return colors[label] || '#f99cc9';
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

  checkIfSaved(techniqueId: string) {
    this.webService.getSavedTechniques().subscribe({
      next: (savedTechniques: any[]) => {
        this.technique.isSaved = savedTechniques.some(t => t._id == techniqueId);
      },
      error: (err) => console.error("Could not verify saved status", err)
    });
  }

  saveToLibrary() {
    if (!this.auth.isLoggedIn()) {
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

  requestAIAnalysis() {
    if (!this.technique?._id) return;

    this.webService.requestAIAnalysis(this.technique._id).subscribe({
      next: () => {
        this.technique.analysis_status = 'processing';
        this.startPollingAnalysis();
      },
      error: (err) => this.backendError = err.error?.error || 'Could not start analysis'
    });
  }

  startPollingAnalysis() {
    if (this.pollHandle) clearInterval(this.pollHandle);

    this.pollHandle = setInterval(() => {
      this.webService.getTechnique(this.technique._id).subscribe(res => {
        this.technique = res;

        if (res.analysis_status !== 'processing') {
          clearInterval(this.pollHandle);
          this.pollHandle = null;

          if (res.analysis_status === 'analysed' && res.analysis) {
            this.processAnalysisTimeline(res.analysis);
          }
        }
      });
    }, 3000);
  }
}