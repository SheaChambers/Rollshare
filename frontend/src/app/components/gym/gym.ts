import { Component } from '@angular/core';
import { ActivatedRoute, RouterModule, Router } from '@angular/router';
import { WebService } from '../../services/web-service';
import { AuthService } from '../../services/auth-service';
import { FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import * as L from 'leaflet';
import { GymReviewList } from '../shared/gym-review-list/gym-review-list';
import { GymReviewForm } from '../shared/gym-review-form/gym-review-form';
import { BackButton } from '../shared/back-button/back-button';

const markerIcon = L.icon({
  iconUrl: 'assets/leaflet/marker-icon.png',
  shadowUrl: 'assets/leaflet/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

L.Marker.prototype.options.icon = markerIcon;

/**
 * The Gym component displays detailed information about a gym,
 * including its location on a Leaflet map, photos, reviews,
 * and contact information. Logged-in users may post reviews, and
 * authorised users (admins or gym creators) may edit or delete gyms.
 */
@Component({
  selector: 'app-gym',
  imports: [CommonModule, ReactiveFormsModule, RouterModule, GymReviewList, GymReviewForm, BackButton],
  templateUrl: './gym.html',
  styleUrl: './gym.css',
})
export class Gym {

  /** Gym object returned from the backend */
  gym: any;

  /** List of all reviews for this gym */
  reviews: any[] = [];

  /** Form used for submitting a new review */
  reviewForm: any;

  /** Backend error message */
  backendError: any;

  /** Whether the fullscreen lightbox viewer is active */
  lightboxActive = false;

  /** The currently opened photo in the lightbox */
  selectedPhoto: string | null = null;

  /** Photos selected for upload */
  selectedFiles: File[] = [];

  /** Fallback image used when a photo cannot load */
  fallbackPhoto = "assets/images/no-image.jpg";

  /** Index of the currently displayed photo */
  currentPhotoIndex: number = 0;

  /** Whether the reviews section is visible */
  showReviews = false;

  /** Whether the current user is authorised to edit/delete the gym */
  authorised = false;

  /**
   * Injects required services for route access, API communication,
   * authentication checks, form building, and navigation.
   */
  constructor(
    private route: ActivatedRoute,
    private webService: WebService,
    public auth: AuthService,
    private formBuilder: FormBuilder,
    private router: Router
  ) {}

  /**
   * Loads gym details, initializes the map, fetches reviews,
   * and builds the review submission form.
   */
  ngOnInit() {
    this.reviewForm = this.formBuilder.group({
      rating: ['', Validators.required],
      comment: ['', Validators.required],
    });

    // Load gym details
    this.webService.getGym(this.route.snapshot.paramMap.get('id')!)
      .subscribe((response: any) => {
        this.gym = response;
        
        this.authorised = this.auth.isAdmin() ||
                          response.created_by === this.auth.getUsername();

        // Delay map load until DOM is ready
        setTimeout(() => this.loadMap(), 200);
    });
    
    // Load reviews
    this.webService.getGymReviews(
      this.route.snapshot.paramMap.get('id')!
    ).subscribe((response: any) => {
      this.reviews = response;
    });
  }

  /** Navigates to the gym edit page */
  goToEditGym() {
    this.router.navigate(['/gyms', this.gym._id, 'edit']);
  }

  /**
   * Initializes the Leaflet map at the gym's coordinates.
   */
  loadMap() {
    if (!this.gym) return;

    const lat = this.gym.geo_location.coordinates[1];
    const lng = this.gym.geo_location.coordinates[0];

    const map = L.map('gym-map', {
      center: [lat, lng],
      zoom: 14,
      zoomControl: true
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
    }).addTo(map);

    L.marker([lat, lng]).addTo(map);
  }

  /**
   * Formats a photo URL for display, determining whether the
   * photo is a complete URL or stored on the RollShare server.
   */
  formatPhotoUrl(photo: any): string {
    if (typeof photo === "string" && photo.startsWith("http")) {
      return photo;
    }
    if (typeof photo === "string") {
      return photo;
    }
    return this.fallbackPhoto;
  }

  /**
   * Handles the selection of new photos for upload.
   */
  onFileChange(event: Event) {
    let input = event.target as HTMLInputElement;
    if (input.files) this.selectedFiles = Array.from(input.files);
  }

  /**
   * Uploads selected photos to the backend and updates the
   * displayed photo list.
   */
  savePhotos() {
    if (!this.gym?._id || this.selectedFiles.length === 0) return;

    this.webService.uploadGymPhotos(this.gym._id, this.selectedFiles)
      .subscribe({
        next: (response: any) => {
          if (!this.gym.photos) this.gym.photos = [];
          
          if (response.photos) {
            this.gym.photos.push(...response.photos);
          }

          this.selectedFiles = [];
        },
        error: err => console.log(err)
      });
  }

  /** Opens the lightbox viewer on a specific photo */
  openPhoto(photo: string) {
    this.currentPhotoIndex = this.gym.photos.indexOf(photo);
    this.selectedPhoto = this.formatPhotoUrl(photo);
    this.lightboxActive = true;
  }

  /** Closes the photo viewer */
  closePhoto() {
    this.lightboxActive = false;
    this.selectedPhoto = null;
  }

  /** Opens the gallery starting from a default index */
  openGallery() {
    this.currentPhotoIndex = 2;
    let photo = this.gym.photos[this.currentPhotoIndex];
    this.selectedPhoto = this.formatPhotoUrl(photo);
    this.lightboxActive = true;
  }

  /** Displays the next image in the gallery */
  nextPhoto() {
    if (!this.gym?.photos?.length) return;

    this.currentPhotoIndex = (this.currentPhotoIndex + 1) % this.gym.photos.length;
    this.selectedPhoto = this.formatPhotoUrl(this.gym.photos[this.currentPhotoIndex]);
  }

  /** Displays the previous image in the gallery */
  previousPhoto() {
    if (!this.gym?.photos?.length) return;

    this.currentPhotoIndex =
      (this.currentPhotoIndex - 1 + this.gym.photos.length) % this.gym.photos.length;
    
    this.selectedPhoto = this.formatPhotoUrl(this.gym.photos[this.currentPhotoIndex]);
  }

  /**
   * Deletes a photo from both backend storage and the UI.
   */
  deletePhoto(photo: string) {
    if (!this.authorised) return;

    let cleanPath = photo.split('?')[0];

    if (cleanPath.includes('/videos/')) {
      cleanPath = cleanPath.split('/videos/')[1];
    }

    this.webService.deleteGymPhoto(this.gym._id, cleanPath)
      .subscribe({
        next: () => {
          this.gym.photos = this.gym.photos.filter((p: string) => p !== photo);
        }
      });
  }

  /** Replaces a failed photo load with a fallback image */
  onPhotoError(event: any) {
    event.target.src = this.fallbackPhoto;
  }

  /** Toggles visibility of the reviews section */
  toggleReviews() {
    this.showReviews = !this.showReviews;
  }

  /** Reloads reviews from the backend */
  refreshReviews() {
    if (!this.gym || !this.gym._id) return;

    this.webService.getGymReviews(this.gym._id).subscribe(response => {
      this.reviews = response;
    });
  }

  /**
   * Handles an emitted event when a review is edited.
   */
  onEditReview(updatedReview: any) {
    this.webService.editGymReview(this.gym._id, updatedReview._id, updatedReview)
      .subscribe(() => this.refreshReviews());
  }

  /**
   * Handles deletion of a review from the backend.
   */
  onDeleteReview(review: any) {
    this.webService.deleteGymReview(this.gym._id, review._id)
      .subscribe(() => this.refreshReviews());
  }
}
