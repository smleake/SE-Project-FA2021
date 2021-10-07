import React, { useEffect, useState } from "react";
import { Redirect, Link } from 'react-router-dom';
import DatePicker from "react-datepicker";
import 'react-datepicker/dist/react-datepicker.css'
import './ReserveTable.scss'

const ReserveTable = () => {

  const [nameState, setNameState] = useState("")
  const [numberState, setNumberState] = useState("")
  const [emailState, setEmailState] = useState("")
  const [dateState, setDateState] = useState(null)
  const [numGuestsState, setNumGuestsState] = useState(0)

  const handleReserve = () => {
    return
  }


    return(
      <div>
      <div className="reserveTable">
          <div className="reserveTable__container">
          <div className="title">
          <h1>ReserveTable</h1>
          </div>
              <div className="formbox">
              <div className= "in">
                  <label>Name:</label>
                  <input className="nameInput"
                      type="text"
                      name="name"
                      id="name"
                      value={nameState}
                      onChange={(e)=>setNameState(e.target.value)}
                  />
              </div>
              <div className= "in">
                  <label>Phone Number:</label>
                  <input className="numberInput"
                      type="text"
                      name="number"
                      id="number"
                      value={numberState}
                      onChange={(e)=>setNumberState(e.target.value)}
                  />
              </div>
              <div className= "in">
                  <label>Email:</label>
                  <input className="emailInput"
                      type="text"
                      name="email"
                      id="email"
                      value={emailState}
                      onChange={(e)=>setEmailState(e.target.value)}
                  />
              </div>
              <div className= "in">
              <label>Reservation Time:</label>
                    <DatePicker
                        name="reservationDate"
                        id="reservationDate"
                        showTimeSelect
                        onChange={setDateState}
                        dateFormat="MM/dd/yy, h:mm aa"
                        selected={dateState}
                        minDate={new Date()}
                    />
              </div>
              <div className= "in">
              <label>Number of Guests:</label>
                  <input className="numGuestsInput"
                      type="number"
                      name="numGuests"
                      id="numGuests"
                      value={numGuestsState}
                      onChange={(e)=>setNumGuestsState(e.target.value)}
                  />
              </div>
              </div>
              <div className="button">
                  <input 
                      className="reserveButton"
                      type= "button" 
                      value="Reserve"
                      onClick={handleReserve}
                  />
              </div>
          </div>

      </div>
      </div>
  );
}

export default ReserveTable;