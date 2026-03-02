import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { WebService } from '../../services/web-service';
import { AuthService } from '../../services/auth-service';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './home.html',
  styleUrls: ['./home.css']
})
export class Home {

  featuredTechnique: any = null;
  savedTechniques: any[] = [];
  nearbyGyms: any[] = [];
  
  searchForm!: FormGroup;
  isLoading = true;

  constructor(
    private webService: WebService,
    public auth: AuthService,
    private fb: FormBuilder,
    private router: Router
  ) {}

  ngOnInit(): void {

    this.searchForm = this.fb.group({
      query: ['']
    });

    this.loadHomepageData();

    this.searchForm.get('query')?.valueChanges.pipe(
      debounceTime(500),
      distinctUntilChanged()
    ).subscribe(value => {
      this.executeSearch(value);
    });
  }

  loadHomepageData() {
    this.isLoading = true;

    this.webService.getTechniques(1, 1).subscribe({
      next: (data) => {
        this.featuredTechnique = data.techniques[0];
        if (this.auth.isLoggedIn() && this.featuredTechnique) {
          this.checkIfSaved(this.featuredTechnique._id);
        }
        this.isLoading = false;
      }
    });

    this.webService.getGyms(1, 3).subscribe({
      next: (data) => this.nearbyGyms = data.gyms
    });

    if (this.auth.isLoggedIn()) {
      this.webService.getSavedTechniques().subscribe({
        next: (data) => this.savedTechniques = data
      });
    }
  }

  executeSearch(q: string) {
    if (!q.trim()) {
      this.loadHomepageData();
      return;
    }

    this.webService.getTechniquesSearch(q).subscribe({
      next: (data) => {
        if (data.techniques && data.techniques.length > 0) {
          const firstMatch = data.techniques[0];
          
          this.router.navigate(['/techniques/category', firstMatch.category], { 
            queryParams: { highlight: firstMatch._id } 
          });
        }
      }
    });
  }

  checkIfSaved(techniqueId: string) {
    this.webService.getSavedTechniques().subscribe({
      next: (savedTechniques: any[]) => {
        this.featuredTechnique.isSaved = savedTechniques.some(t => t._id == techniqueId);
      },
      error: (err) => console.error("Could not verify saved status", err)
    });
  }

  toggleLike(event: Event) {
    event.stopPropagation();

    if (!this.auth.isLoggedIn()) {
      alert("Please log in to like techniques");
      return;
    }

    this.webService.toggleLike(this.featuredTechnique._id)
      .subscribe((res: any) => {
        if (!this.featuredTechnique.likes) {
          this.featuredTechnique.likes = [];
        }

        const username = this.auth.getUsername();

        if (res.liked) {
          this.featuredTechnique.likes.push(username);
        } else {
          this.featuredTechnique.likes = 
            this.featuredTechnique.likes.filter((u: string) => u !== username);
        }
      });
  }

  toggleSave(event: Event) {
    event.stopPropagation();

    if (!this.auth.isLoggedIn()) {
      alert("Please log in to save techniques!");
      return;
    }

    if (this.featuredTechnique.isSaved) {
      this.webService.unsaveTechnique(this.featuredTechnique._id)
        .subscribe(() =>
          this.featuredTechnique.isSaved = false);
    } else {
      this.webService.saveTechnique(this.featuredTechnique._id)
        .subscribe(() => 
          this.featuredTechnique.isSaved = true);
    }
  }

  goToTechnique(id: string) {
    this.router.navigate(['/techniques/', id]);
  }

  goToSavedTechniques() {
    this.router.navigate(['/training']);
  }

  goToGyms() {
    this.router.navigate(['/community']);
  }
}