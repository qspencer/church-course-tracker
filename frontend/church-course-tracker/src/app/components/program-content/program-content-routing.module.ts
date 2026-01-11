import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ProgramContentComponent } from './program-content.component';

const routes: Routes = [
  {
    path: '',
    component: ProgramContentComponent
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class ProgramContentRoutingModule { }


