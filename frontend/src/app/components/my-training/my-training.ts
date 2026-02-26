import { Component, OnInit, Input } from '@angular/core';
import { ActivatedRoute, RouterModule, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { WebService } from '../../services/web-service';
import { AuthService } from '../../services/auth-service';
import { HttpClient } from '@angular/common/http';
import { TechniqueCard } from '../shared/technique-card/technique-card';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-my-training',
  imports: [RouterModule, CommonModule, TechniqueCard, FormsModule],
  templateUrl: './my-training.html',
  styleUrl: './my-training.css',
})
export class MyTraining {

  techniques: any [] = [];
  isMyRollsMode: boolean = true;
  backendError: string | null = null;
  displayRolls: any[] = [];
  displayTechniques: any[] = [];

  /** Techniques after applying all frontend filters and sorting */
  filteredRolls: any[] = [];

  /** Controls the visibility of the filter sidebar */
  filtersOpen = false;

  /** Current sorting method */
  sortBy = "Most Recent";

  constructor(
    private http: HttpClient, 
    private router: Router,
    private webService: WebService
  ) {}

  ngOnInit() {
    this.loadData();
  }

  setMode(mode: boolean) {
    this.isMyRollsMode = mode;
    this.loadData();
  }

  toggleMode() {
    this.isMyRollsMode = !this.isMyRollsMode;
    this.backendError = null;
    this.loadData();
  }

  fetchTechniques() {
    this.webService
      .getMyRolls()
      .subscribe((response: any) => {
        this.techniques = response.techniques || [];
      });
  }

  loadData() {
    if (this.isMyRollsMode) {
      this.webService.getMyRolls().subscribe({
        next: (data) => {
          this.displayRolls = data.techniques || (Array.isArray(data) ? data : []);

          console.log("Final displayData:", this.displayRolls);
          this.applyFrontendFilters();
          console.log("Filtered: ", this.filteredRolls);
        },
        error: (err) => {
          console.error("API Error:", err);
          this.backendError = "Could not load your rolls";
        }
      });
    } else {
      this.webService.getSavedTechniques().subscribe({
        next: (data) => {
          this.displayTechniques = data.techniques || (Array.isArray(data) ? data : []);

          console.log("Final DisplayData: ", this.displayTechniques);
        },
        error: (err) => {
          console.error("API Error:", err);
          this.backendError = "Could not load your saved techniques";
        }
      })
    }

  }

  viewTechnique(id: string) {
    if (id) {
      this.router.navigate(['/techniques', id]);
    } else {
      console.error("Could not navigate: Technique ID is missing.");
    }
  }

  /** Toggles the filter panel open/closed */
  toggleFilters() {
    this.filtersOpen = !this.filtersOpen;
  }

  /**
   * Applies tag filters (popular, highRated), sorting,
   * and updates the final filtered list of techniques.
   */
  private applyFrontendFilters() {
    let list = [...this.displayRolls];

    switch (this.sortBy) {
      case "Most Recent":
        list.sort((a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
        break;

      case "A-Z":
        list.sort((a, b) => a.name.localeCompare(b.name));
        break;

      case "Highest Rated":
        list.sort((a, b) => {
          const getAvg = (item: any) => {
            if (!item.reviews || item.reviews.length === 0) return 0;
            
            const totalStars = item.reviews.reduce((sum: number, r: any) => {
              return sum + Number(r.stars || r.rating || 0); 
            }, 0);
            
            return totalStars / item.reviews.length;
          };

          const scoreA = getAvg(a);
          const scoreB = getAvg(b);
          
          return scoreB - scoreA;
        });
        break;

      case "Most Reviewed":
        list.sort((a, b) =>
          (b.reviews?.length ?? 0) - (a.reviews?.length ?? 0)
        );
        break;
    }

    this.filteredRolls = list;
  }

  /**
   * Applies filters and reloads the first page of results.
   */
  applyFilters() {
    this.applyFrontendFilters();
    this.filtersOpen = false;
  }

  /** Resets all user-applied filters and search text */
  resetFilters() {
    this.sortBy = "Most Recent";
    this.applyFilters();
  }
}
