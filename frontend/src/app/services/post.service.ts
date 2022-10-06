import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { last, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PostService {
  //private url : string = 'https://zenpanda.uk/api';
  private url : string = 'http://localhost:5000';
   

  constructor(private httpClient: HttpClient) { }

  post_init(uuid : string, playerSide : number):Observable<any>{
    return this.httpClient.post(
      this.url + "/initPlayer", {'uuid' : uuid, 'playerSide': playerSide});
    }
  

  post_turn(uuid: string, lastMove: number):Observable<any>{
    return this.httpClient.post(
      this.url + "/gameTurn", {'uuid' : uuid, 'lastMove': lastMove});
    }
  }

