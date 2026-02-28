import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { WebService } from '../../services/web-service';
import { AuthService } from '../../services/auth-service';
import { FormsModule } from '@angular/forms';
import { TechniqueCard } from '../shared/technique-card/technique-card';

/**
 * The CategoryTechniques component displays a list of techniques
 * belonging to a specific category. It supports searching,
 * filtering by difficulty and tags, client-side sorting,
 * and paginated browsing.
 */
@Component({
  selector: 'app-category-techniques',
  imports: [CommonModule, FormsModule, TechniqueCard],
  templateUrl: './category-techniques.html',
  styleUrl: './category-techniques.css',
})
export class CategoryTechniques {
  
  /** The technique category extracted from the route */
  category: string = "";

  /** Raw techniques returned from the backend */
  techniques: any[] = [];

  /** Techniques after applying all frontend filters and sorting */
  filteredTechniques: any[] = [];

  isLoading: boolean = true;

  /** Controls the visibility of the filter sidebar */
  filtersOpen = false;

  /** Search input text */
  searchTerm = "";

  /** Selected difficulty filters */
  selectedDifficulties: string[] = [];

  /** Selected tag filters (popular, highRated, verified) */
  selectedTags: string[] = [];

  /** Current sorting method */
  sortBy = "name";

  /** Current page index */
  page = 1;

  /** Number of items displayed per page */
  pageSize = 9;

  /** Total number of available pages */
  totalPages = 1;

  /** Total number of techniques returned by the backend */
  totalItems = 0;

  /**
   * Creates an instance of CategoryTechniques.
   * @param route Used to extract the category from the URL.
   * @param webService Service used for API calls.
   * @param router Handles navigation to technique details.
   */
  constructor(
    private route: ActivatedRoute,
    private webService: WebService,
    private router: Router,
    public auth: AuthService
  ) {}

  /**
   * Initializes the component by reading the category
   * and fetching the first page of techniques.
   */
  ngOnInit() {
    this.route.paramMap.subscribe(params => {
    this.category = params.get('category') || "";
    this.page = 1; // reset pagination on category change
    this.fetchTechniques();
  });
  }

  /** Toggles the filter panel open/closed */
  toggleFilters() {
    this.filtersOpen = !this.filtersOpen;
  }

  /** Model used for difficulty checkbox UI */
  selectedDifficultiesModel: any = {
    Beginner: false,
    Intermediate: false,
    Advanced: false
  };

  /**
   * Updates the list of selected difficulties 
   * based on the checkbox model.
   */
  toggleDifficultyModel(diff: string) {
    this.selectedDifficulties = Object.keys(this.selectedDifficultiesModel)
      .filter(key => this.selectedDifficultiesModel[key]);
  }

  /** Model used for tag filters (popular, highRated, verified) */
  selectedTagsModel: any = {
    verified: false,
    popular: false,
    highRated: false
  };

  /**
   * Updates the list of selected tag filters 
   * based on the checkbox model.
   */
  toggleTagModel(tag: any) {
    this.selectedTags = Object.keys(this.selectedTagsModel)
      .filter(key => this.selectedTagsModel[key]);
  }

  /**
   * Fetches a page of techniques from the backend using filters.
   * Applies client-side sorting and tag filtering afterwards.
   */
  fetchTechniques() {
    this.isLoading = true;
    let filters: any = {
      q: this.searchTerm.trim(),
      difficulty: this.selectedDifficulties
    };

    this.webService
      .getTechniquesByCategory(this.category, this.page, this.pageSize, filters)
      .subscribe((response: any) => {
        const categoryTech = response.techniques || [];

        const pag = response.pagination;
        if (pag) {
          this.page = pag.page;
          this.pageSize = pag.page_size;
          this.totalItems = pag.total_items;
          this.totalPages = pag.total_pages;
        }

        if (this.auth.isLoggedIn()) {
          this.webService.getSavedTechniques().subscribe({
            next: (savedData: any) => {
              const savedList = savedData.techniques || (Array.isArray(savedData) ? savedData : []);
              const savedIds = savedList.map((s: any) => s._id);

              this.techniques = categoryTech.map((t: any) => ({
                ...t,
                isSaved: savedIds.includes(t._id)
              }));

              this.applyFrontendFilters();
              this.isLoading = false;
            },
            error: () => {
              this.techniques = categoryTech;
              this.applyFrontendFilters();
              this.isLoading = false;
            }
          });
        } else {
          this.techniques = categoryTech;
          this.applyFrontendFilters();
          this.isLoading = false;
        }
      });
  }

  /**
   * Applies tag filters (popular, highRated), sorting,
   * and updates the final filtered list of techniques.
   */
  private applyFrontendFilters() {
    let list = [...this.techniques];

    // Filter popular techniques (at least 5 reviews)
    if (this.selectedTags.includes("popular")) {
      list = list.filter(t => (t.reviews?.length || 0) >= 5);
    }

    // Filter high-rated techniques (avg >= 4)
    if (this.selectedTags.includes("highRated")) {
      list = list.filter(t => this.averageRating(t) >= 4);
    }

    // Sorting options
    if (this.sortBy === "name") {
      list.sort((a, b) => a.name.localeCompare(b.name));
    } else if (this.sortBy === "rating") {
      list.sort((a, b) => this.averageRating(b) - this.averageRating(a));
    } else if (this.sortBy === "popularity") {
      list.sort((a, b) => (b.reviews?.length || 0) - (a.reviews?.length || 0));
    } else if (this.sortBy === "difficulty") {
      const order = ["Beginner", "Intermediate", "Advanced"];
      list.sort((a, b) => order.indexOf(a.difficulty) - order.indexOf(b.difficulty));
    }

    this.filteredTechniques = list;
  }

  /**
   * Applies filters and reloads the first page of results.
   */
  applyFilters() {
    this.page = 1;
    this.fetchTechniques();
    this.filtersOpen = false;
  }

  /** Resets all user-applied filters and search text */
  resetFilters() {
    this.searchTerm = "";
    this.selectedDifficulties = [];
    this.selectedTags = [];
    this.sortBy = "name";
    this.applyFilters();
  }

  /** Loads the next page of techniques */
  nextPage() {
    if (this.page < this.totalPages) {
      this.page++;
      this.fetchTechniques();
    }
  }

  /** Loads the previous page of techniques */
  previousPage() {
    if (this.page > 1) {
      this.page--;
      this.fetchTechniques();
    }
  }

  /**
   * Navigates to a specific technique's detail page.
   * @param id Technique ID
   */
  goToTechnique(id: string) {
    this.router.navigate(['/techniques/', id]);
  }

  /**
   * Computes the average rating for a technique.
   * @param t Technique object
   * @returns A number between 0 and 5
   */
  averageRating(t: any): number {
    let reviews = t.reviews || [];
    if (!reviews.length) return 0;
    let total = reviews.reduce((sum: number, r: any) => sum + Number(r.rating), 0);
    return total / reviews.length;
  }

  /**
   * Fallback handler when an image fails to load.
   * Attempts alternate YouTube thumbnails or falls back to a default image.
   */
  onImageError(event: any) {
    const img = event.target;

    if (img.src.includes("hqdefault")) {
      img.src = img.src.replace("hqdefault.jpg", "default.jpg");
    } else {
      img.src = "assets/images/no-image.jpg";
    }
  }
}
