import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { WebService } from '../../services/web-service';
import { AuthService } from '../../services/auth-service';
import { TechniqueCard } from '../shared/technique-card/technique-card';
import { GymCard } from '../shared/gym-card/gym-card';

@Component({
  selector: 'app-community',
  standalone: true,
  imports: [CommonModule, TechniqueCard, GymCard],
  templateUrl: './community.html',
  styleUrl: './community.css'
})
export class Community {

  activeTab: 'feed' | 'friends' | 'clubs' = 'feed';
  
  communityPosts: any[] = [];
  communityClubs: any[] = [];

  currentPage: number = 1;
  pageSize: number = 9;
  
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
    let filters: any = {};

    this.webService.getGyms(this.currentPage, this.pageSize, filters).subscribe({
      next: (response) => {
        this.communityClubs = response.gyms || [];
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
}