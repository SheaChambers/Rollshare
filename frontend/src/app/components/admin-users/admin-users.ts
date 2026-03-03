import { Component, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AgGridAngular } from 'ag-grid-angular';
import { ColDef } from 'ag-grid-community';
import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community';
import { WebService } from '../../services/web-service';
import { BackButton } from '../shared/back-button/back-button';

ModuleRegistry.registerModules([AllCommunityModule]);

@Component({
  selector: 'app-admin-users',
  imports: [CommonModule, AgGridAngular, BackButton],
  templateUrl: './admin-users.html',
  styleUrls: ['./admin-users.css']
})
export class AdminUsers {

  rowData: any[] = [];

  @ViewChild(AgGridAngular) agGrid!: AgGridAngular;

  pagination = true;
  paginationPageSize = 10;
  paginationPageSizeSelector = [10, 25, 50];

  columnDefs: ColDef[] = [
    { field: "username", flex: 2, minWidth: 120, filter: true },
    { field: "email", hide: window.innerWidth < 400, flex: 3, filter: true },
    {
      field: "banned",
      headerName: "St.",
      width: 80,
      valueGetter: (params) =>
        params.data.banned ? "Banned" : "Active",
      cellStyle: (params) => ({
        color: params.value === "Banned" ? "red" : "green",
        fontWeight: "bold"
      })
    },
    {
      headerName: "Action",
      width: 80,
      cellRenderer: (params: any) => {
        const button = document.createElement("button");
        button.innerText = params.data.banned ? "Unban" : "Ban";
        button.className = params.data.banned ? "btn-primary" : "btn-danger";

        button.addEventListener("click", () => {
          this.toggleBan(params.data);
        });

        return button;
      }
    }
  ];

  constructor(private webService: WebService) {}

  ngOnInit() {
    this.loadUsers();
  }

  loadUsers() {
    this.webService.getAllUsers().subscribe((data: any) => {
      this.rowData = data;
    });
  }

  toggleBan(user: any) {

    const request = user.banned
      ? this.webService.unbanUser(user._id)
      : this.webService.banUser(user._id);

    request.subscribe(() => {

      user.banned = !user.banned;

      this.agGrid.api.applyTransaction({
        update: [user]
      });

    });
  }
}