import { TitleCasePipe } from '@angular/common';
import { createInjectableType } from '@angular/compiler';
import {Title} from "@angular/platform-browser";
import {Component, OnInit, EventEmitter, Input, OnDestroy} from '@angular/core';
import { UntypedFormBuilder } from '@angular/forms';
import { identity } from 'rxjs';
import { BoardComponent, TurnData } from './board/board.component';
import { PostService } from './services/post.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})



export class AppComponent implements OnInit {
  posts:any;
  uuid : string = "";

  currentTurn = true;
  public playerSide = Math.floor(Math.random()*2)?-1:1;
  lastMove: number = 0;
  public gridUpdate : [number, number] = [0,0];
  public currentWin : number = 0;
  public initGrid : number[][] = [[],[],[],[],[],[]];

  constructor(private service:PostService, private titleService:Title) {
    this.titleService.setTitle("Connect 4");
  }







  ngOnInit() {
    //Set title
    

    //Get UUID
    let sesId = sessionStorage.getItem("uuid")
    console.log(sesId)
    if(sesId!="undefined"){
      this.uuid = sesId!;
    }

    this.service.post_init(this.uuid, this.playerSide)
    .subscribe(response => {
      this.uuid = response["uuid"]
      this.playerSide = response["playerSide"]
      sessionStorage.setItem("uuid", response["uuid"]); //Uncomment on Release
      this.initGrid = response["grid"];
      console.log(response)

    });
}


  clearSession(){
    sessionStorage.clear();
    window.location.reload();
  }


  onTurn(turn: TurnData) {
    this.currentTurn = turn.currentTurn;
    this.lastMove = turn.lastMove;
    this.service.post_turn(this.uuid, this.lastMove)
    .subscribe(response => {this.currentWin = response["win"]; this.gridUpdate = response["newGrid"];});
    this.currentTurn = true;

    console.log(this.gridUpdate);
    
    
  }


}

