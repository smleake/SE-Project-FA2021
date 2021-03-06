import React, { useEffect, useState } from "react";
import './Register.scss'
import { Redirect, Link } from 'react-router-dom';
import { checkAuth, setAuth } from '../../verifyLogin';

const Register = () => {

    const [usernameState, setUsernameState] = useState("")
    const [passwordState, setPasswordState] = useState("")
    const [confirmPasswordState, setConfirmPasswordState] = useState("")

    const handleSubmit = (e) => {
        e.preventDefault()

        if(passwordState === confirmPasswordState && usernameState !== ''){
            const formData = new FormData();

            formData.append('username', usernameState)
            formData.append('password', passwordState)

            fetch(`${process.env.API_URL}/api/register`,
            {
              method: 'POST',
              body: formData,
            }
          )
            .then(res => {
              if(!res.ok) {
                console.log(res)
                console.log(res.status)
              }
              if (res.status === 403) {
                alert("Username taken!");
                throw Error('Could not fetch the data for that resource');
              }
              return res.json();
            })
            .then(res => {
              setAuth(res)
              if (checkAuth())
                window.location.assign("/profile")
            })
            .catch((error) => {
              console.error('Error: ', error);
            })

        }
        else if (usernameState === ''){
            alert("Username can not be blank")
        }
        else if (passwordState !== confirmPasswordState){
            alert("Passwords do not match")
        }
        else if (passwordState === ''){
            alert("Password can not be blank")
        }

        };

    return(
        <div>
        <div className="register">
            <div className="register__container">
            <div className="title">
            <h1>Register</h1>
            </div>
            <form onSubmit = {handleSubmit}>
                <div className="formbox">
                    <div className= "in">
                        <label>Username:</label>
                        <input className="usernameInput"
                            type="text"
                            name="username"
                            id="username"
                            value={usernameState}
                            onChange={(e)=>setUsernameState(e.target.value)}
                        />
                    </div>
                    <div className= "in">
                        <label>Password:</label>
                            <input className="add"
                                type="password"
                                name="pass"
                                id="pass"
                                value = {passwordState}
                                onChange={(e)=>setPasswordState(e.target.value)}
                            />
                    </div>
                        <div className ="in">
                            <label>Confirm Password:</label>
                                <input className="add"
                                    type="password"
                                    name="pass"
                                    id="pass"
                                    value = {confirmPasswordState}
                                    onChange={(e)=>setConfirmPasswordState(e.target.value)}
                                />
                        </div>
                </div>
                <div className="button">
                    <input 
                        className="registerButton"
                        type= "submit" 
                        value="Register"
                    />
                </div>
                </form>
            </div>

        </div>
            <div className="loginLink">
                    <label>Already have an account? Click{'\u00A0'}</label>
                        <Link to="/login">here</Link>
            </div>
        </div>
    );
}

export default Register;