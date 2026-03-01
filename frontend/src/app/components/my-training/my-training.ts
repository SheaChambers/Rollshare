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
        next: (rollsData) => {
          const rolls = rollsData.techniques || (Array.isArray(rollsData) ? rollsData : []);

          this.webService.getSavedTechniques().subscribe({
            next: (savedData: any) => {
              const savedList = savedData.techniques || (Array.isArray(savedData) ? savedData : []);
              const savedIds = savedList.map((s: any) => s._id);

              this.displayRolls = rolls.map((r: any) => ({
                ...r,
                isSaved: savedIds.includes(r._id)
              }));

              this.applyFrontendFilters();
            },
            error: (err) => console.error("Error fetching saved list", err)
          });
        },
        error: (err) => {
          this.backendError = "Could not load your rolls";
          console.error("API Error:", err);
        }
      });
    } else {
      this.webService.getSavedTechniques().subscribe({
        next: (data) => {
          const savedList = data.techniques || (Array.isArray(data) ? data : []);

          this.displayTechniques = savedList.map((t: any) => ({
            ...t,
            isSaved: true
          }));
        },
        error: (err) => {
          this.backendError = "Could not load your saved techniques";
          console.error("API Error:", err);
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
    let sourceList = this.isMyRollsMode ? this.displayRolls : this.displayTechniques;
    let list = [...sourceList];

    switch (this.sortBy) {
      case "Most Recent":
        list.sort((a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
        break;

      case "A-Z":
        list.sort((a, b) => a.name.localeCompare(b.name));
        break;

      case "Most Liked":
        list.sort((a, b) =>
          (b.likes?.length ?? 0) - (a.likes?.length ?? 0)
        );
        break;

      case "Most Reviewed":
        list.sort((a, b) =>
          (b.reviews?.length ?? 0) - (a.reviews?.length ?? 0)
        );
        break;
    }

    if (this.isMyRollsMode) {
      this.filteredRolls = list;
    } else {
      this.displayTechniques = list;
    }
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
