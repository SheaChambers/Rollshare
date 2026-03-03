import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-banned',
  imports: [CommonModule],
  templateUrl: './banned.html',
  styleUrls: ['./banned.css']
})
export class Banned {

  bannedInfo: any = null;

  constructor (private router: Router) {}

  ngOnInit() {
    const stored = sessionStorage.getItem('bannedInfo');
    if (stored) {
      this.bannedInfo = JSON.parse(stored);

      if (this.bannedInfo.banned_at) {
        this.bannedInfo.banned_at = new Date(this.bannedInfo.banned_at);
      }
    }
  }

  goToHome() {
    this.router.navigate(['/']);
  }
}