import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { WebService } from '../../services/web-service';
import { AuthService } from '../../services/auth-service';
import { TechniqueCard } from '../shared/technique-card/technique-card';
import { GymCard } from '../shared/gym-card/gym-card';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-community',
  standalone: true,
  imports: [CommonModule, TechniqueCard, GymCard, FormsModule],
  templateUrl: './community.html',
  styleUrl: './community.css'
})
export class Community {

  activeTab: 'feed' | 'friends' | 'clubs' = 'feed';
  
  communityPosts: any[] = [];
  communityClubs: any[] = [];

  filteredClubs: any[] = [];
  filtersOpen = false;
  cityCache: any = {};
  cityList : string[] = [];
  searchTerm = "";
  sortBy = "name";
  selectedCities: string[] = [];
  selectedTags: string[] = [];

  currentPage: number = 1;
  pageSize: number = 9;

  pagination: any = {
    page: 1,
    total_pages: 1,
    has_next: false,
    has_previous: false
  };
  
  errorMessage: string | null = null;
  isLoading: boolean = true;

  constructor(
    private router: Router,
    private webService: WebService,
    public auth: AuthService
  ) {}

  ngOnInit(): void {
    this.loadDiscoveryFeed();
  }

  /**
   * Fetches the global activity feed. 
   * In a real app, you might have a dedicated /community/feed endpoint,
   * but for now, we can fetch all public techniques.
   */
  loadDiscoveryFeed() {
    this.isLoading = true;
    this.webService.getTechniques(this.currentPage, this.pageSize).subscribe({
      next: (response: any) => {
        const data = Array.isArray(response) ? response : response.techniques;

        if (this.auth.isLoggedIn()) {
          this.webService.getSavedTechniques().subscribe({next: (saved) => {
            const savedList = Array.isArray(saved) ? saved : (saved.techniques || []);
            const savedIds = savedList.map((s: any) => s._id);
            
            this.communityPosts = data.map((post: any) => ({
              ...post,
              _id: post._id.toString(),
              isSaved: savedIds.includes(post._id)
            }));
            this.isLoading = false;
          }});
        }
      },
      error: (err) => {
        this.errorMessage = "Failed to load the activity feed.";
        this.isLoading = false;
        console.error(err);
      }
    });
  }

  loadClubs() {
    this.isLoading = true;
    const backendSortBy = 'name';
    const backendVerified =
      this.selectedTags.includes('verified') ? 'true' : '';

    const filters = {
      q: this.searchTerm.trim(),
      verified: backendVerified,
      sort_by: backendSortBy,
      order: 'asc'
    };

    this.webService.getGyms(this.currentPage, this.pageSize, filters).subscribe({
      next: (response) => {
        console.log("Full Backend Response:", response);
        this.communityClubs = response.gyms || [];
        this.pagination = response.pagination;

        this.communityClubs.forEach(club => this.reverseLookupCity(club));

        this.applyFrontendFilters();

        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage = "Could not load gyms.";
        this.isLoading = false;
      }
    });
  }

  /**
   * Logic for switching tabs
   */
  switchTab(tab: 'feed' | 'friends' | 'clubs') {
    this.activeTab = tab;
    if (tab === 'feed') {
      this.loadDiscoveryFeed();
    }
    if (tab === 'clubs') {
      this.loadClubs();
    }
  }

  goToAddGym() {
    this.router.navigate(['/gyms/new']);
  }

  /** Toggles the visibility of the filter panel */
  toggleFilters() {
    this.filtersOpen = !this.filtersOpen;
  }

  /** Handles multi-city checkbox changes */
  toggleCitySelection(event: any) {
    const city = event.target.value;

    if (event.target.checked) {
      this.selectedCities.push(city);
    } else {
      this.selectedCities = this.selectedCities.filter(c => c !== city);
    }
  }

  /** Handles tag filter checkboxes (popular, verified, multiCoach) */
  toggleTag(event: any) {
    const tag = event.target.value;

    if (event.target.checked) {
      this.selectedTags.push(tag);
    } else {
      this.selectedTags = this.selectedTags.filter(t => t !== tag);
    }
  }

  /**
   * Applies backend + frontend filters and refreshes the gym list.
   */
  applyFilters() {
    this.currentPage = 1;
    this.loadClubs();
    this.filtersOpen = false;
  }

  /**
   * Applies the advanced frontend-only filtering logic such
   * as multi-city, popular, multi-coach, rating sorting, and
   * popularity sorting. This acts on the results returned by backend pagination.
   */
  private applyFrontendFilters() {
    let gyms = [...this.communityClubs];

    // Multi-city filter
    if (this.selectedCities.length > 0) {
      gyms = gyms.filter(gym => {
        const city = this.cityCache[gym._id];
        return city ? this.selectedCities.includes(city) : true;
      });
    }

    // “Popular” ⇒ gyms with at least 5 reviews
    if (this.selectedTags.includes("popular")) {
      gyms = gyms.filter(gym => gym.reviews?.length >= 5);
    }

    // “MultiCoach” ⇒ gyms with at least 3 coaches
    if (this.selectedTags.includes("multiCoach")) {
      gyms = gyms.filter(gym => gym.coaches?.length >= 3);
    }

    // Sorting for name/rating/popularity
    if (this.sortBy === 'name') {
      gyms.sort((a, b) => a.name.localeCompare(b.name));
    } else if (this.sortBy === 'rating') {
      gyms.sort((a, b) => this.averageRating(b) - this.averageRating(a));
    } else if (this.sortBy === 'popularity') {
      gyms.sort((a, b) => (b.reviews?.length || 0) - (a.reviews?.length || 0));
    }

    this.filteredClubs = gyms;
  }

  /**
   * Resets all filters and reloads the first page.
   */
  resetFilters() {
    this.searchTerm = "";
    this.sortBy = "name";
    this.selectedCities = [];
    this.selectedTags = [];
    this.currentPage = 1;
    this.loadClubs();
    this.filtersOpen = false;
  }

  /**
   * Uses reverse geocoding (Nominatim API) to determine the city name
   * from each gym's latitude/longitude. Results are cached.
   */
  reverseLookupCity(gym: any) {
    const lat = gym.geo_location.coordinates[1];
    const lng = gym.geo_location.coordinates[0];

    if (this.cityCache[gym._id]) return;

    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`)
      .then(res => res.json())
      .then(data => {
        const city =
          data.address?.city ||
          data.address?.town ||
          data.address?.village ||
          "Unknown";

        this.cityCache[gym._id] = city;

        if (!this.cityList.includes(city)) {
          this.cityList.push(city);
          this.cityList.sort();
        }

        this.applyFrontendFilters();
      });
  }

  /**
   * Calculates the average rating for a gym from its reviews.
   * @returns The average rating (0–5)
   */
  averageRating(gym: any): number {
    if (!gym.reviews || !gym.reviews.length) return 0;
    const total = gym.reviews.reduce(
      (sum: number, r: any) => sum + Number(r.rating),
      0
    );
    return total / gym.reviews.length;
  }
}