import { style } from '@angular/animations';
import { Component, Output, EventEmitter, Input, OnInit, SimpleChanges } from '@angular/core';
import { ColdObservable } from 'rxjs/internal/testing/ColdObservable';

import { AppComponent } from '../app.component';

@Component({
  selector: 'app-board',
  templateUrl: './board.component.html',
  styleUrls: ['./board.component.css']
})



export class BoardComponent implements OnInit {

  @Input() appComponent!: AppComponent;
  @Input() gridUpdate : [number, number] = [0,0];
  @Input() currentWin : number = 0;
  @Input() initGrid : number[][] = [[],[],[],[],[],[]];
  @Input() playerSide : number = 1;

  currentTurn : boolean = true;
  @Output() turnChanged = new EventEmitter<TurnData>();

  grid : GridSquare[][]= [[],[],[],[],[],[]];



  


  bufferSound(ctx : AudioContext, url : any) {
    var p : Promise<AudioBuffer> = new Promise(function(resolve, reject) {
      var req = new XMLHttpRequest();
      req.open('GET', url, true);
      req.responseType = 'arraybuffer';
      req.onload = function() {
        ctx.decodeAudioData(req.response, resolve, reject);
      }
      req.send();
    });
    return p;
  }

  audioContext : AudioContext = new AudioContext();

  placePiece(column : number){
    if(this.currentWin != 1){
      if(this.currentTurn){
        //Find lowest row in column that is not occupied
        let lowestPoint = this.grid.length;
        for(let l_row = 0; l_row < this.grid.length; l_row++){
          if(this.grid[l_row][column].squareSide === 0){
            lowestPoint = l_row;
          }
          else{
            break;
          }
        }
        if(lowestPoint < this.grid.length){

          let turnData = new TurnData();
          turnData.currentTurn = this.currentTurn
          turnData.lastMove = column
          turnData.playerSide = this.playerSide

          this.grid[lowestPoint][column].squareSide = this.playerSide;
          this.pieceSound();
          this.currentTurn = false;
          this.turnChanged.emit(turnData);
          console.log(this.grid)
        }
      }
    }
  }


  highlightColumn(column : number){
    //For each column
    if(this.currentWin==0){
      for(let row = 0; row < this.grid.length; row++){
        this.grid[row][column].isHighlighted = true;
      }
    }
  }

  
  unHighlightColumn(column : number){
    //For each column
    for(let row = 0; row < this.grid.length; row++){
      this.grid[row][column].isHighlighted = false;
    }
  }




  pieceSound(){
    let audioContext = this.audioContext
    this.bufferSound(this.audioContext, "assets/sounds/646781__pbimal__chess-piece-bounce.ogg").then(function (buffer) {
        var g = audioContext.createGain();
        g.gain.value = 5;
        g.connect(audioContext.destination);
      
        var bq = audioContext.createBiquadFilter();
        bq.connect(g);
      
        var src = audioContext.createBufferSource();
        src.buffer = buffer;
        src.playbackRate.value = Math.random() + 1;
        src.connect(bq);
      
        src.start();
    });
        
    }
  
  ngOnChanges(changes: SimpleChanges) {

    let l_currentWin = changes['currentWin']
    let l_initGrid = changes['initGrid']
    let l_gridUpdate = changes['gridUpdate']


    console.log(changes)

    if(l_initGrid && l_initGrid.currentValue){
      console.log(this.initGrid)
      for(let y = 0; y<this.grid.length; ++y){
        for(let x = 0; x<7; ++x){ //6 per row
          this.grid[y][x] = new GridSquare();
          if(changes['initGrid'].currentValue[y][x]==1){
            this.grid[y][x].squareSide = -this.playerSide
          }
          else if (changes['initGrid'].currentValue[y][x]==-1)
          {
            this.grid[y][x].squareSide = this.playerSide
          }
        }
      }
    }
    if(l_currentWin){
      if(l_currentWin.currentValue != 0){
        this.currentTurn = false;
      }
    }

    if(l_gridUpdate && l_gridUpdate.currentValue != l_gridUpdate.previousValue && this.currentWin != 1){
      let l_gridUpdate = changes['gridUpdate'].currentValue
      console.log(l_gridUpdate)
      this.grid[l_gridUpdate[0]][l_gridUpdate[1]].squareSide = this.playerSide * -1;
      this.pieceSound();
      this.currentTurn = true;
    }






  }


  
  constructor() {}

  ngOnInit(): void {
    for(let y = 0; y<this.grid.length; ++y){
      for(let x = 0; x<7; ++x){ //6 per row
        this.grid[y][x] = new GridSquare();
      }
    }
}
  
}


class GridSquare {

  squareSide : number = 0;
  isHighlighted : boolean = false;
  
}

export class TurnData {
  playerSide = 0
  currentTurn = false
  lastMove: number = 0
}