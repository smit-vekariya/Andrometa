import { Button, Col, Form, Row } from 'antd';
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import logo from "../images/logo-no-background.png";

export default function Register(){
    let navigate = useNavigate()
    const [userValid, setUserValid] = useState(true)
    const [passValid, setPassValid] = useState(true)
    const [matchPassValid, setMatchPassValid] = useState(true)
    const [registerForm, setRegisterForm] = useState({username:"",first_name:"",last_name:"",email:"",password:"",confirm_password:""})
    const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
    const passwordRegex = /^(?=.*\d)(?=.*[a-z])(?=.*[\W_])(?=.*[A-Z]).{6,20}$/
    const handleChange= (e) => {
        setRegisterForm({...registerForm,[e.target.name]:e.target.value})
        if(e.target.name === "username"){
            setUserValid(usernameRegex.test(e.target.value)? true:false)
        }
        if(e.target.name === "password"){
            setPassValid(passwordRegex.test(e.target.value)?true:false)
        }
        if(e.target.name === "confirm_password"){
            setMatchPassValid(registerForm.password === e.target.value?true:false)
        }
    }

    const registerUser = async(e) => {
        e.preventDefault()
        var usernameValid = usernameRegex.test(registerForm.username)? true:false
        var passwordValid = registerForm.password === registerForm.confirm_password?true:false
        if(passwordValid && usernameValid){
            let response = await fetch("http://localhost:8000/account/register/",{
                method:"POST",
                headers:{'Content-Type':"application/json"},
                body:JSON.stringify(registerForm)
            })
            let data = await response.json()
            if (response.status === 200){
                console.log(data)
                navigate("/login")
            }else{
                alert("Something went Wrong!")
            }

        }else{
            setUserValid(usernameValid)
            setMatchPassValid(passwordValid)
            console.log("Something went Wrong on registration")
            return
        }
    }
    return(
        <>
            <div className="home_nav">
                <Link to="/home"><Button variant="outline-dark">Home</Button></Link>
                <Link to="/login"><Button variant="outline-primary">Sign In</Button></Link>
            </div>
            <div className="main_div">
                <div className="login_div">
                    <Form onSubmit={registerUser}>
                        <Form.Group className="mb-3" controlId="formBasicEmail" style={{textAlign:'center'}}>
                            <img src={logo} alt="logo-no-background.png" style={{width:"300px",marginBottom:"15px"}}></img>
                            <h2 className="fontfamily">Create Account</h2>
                        </Form.Group>
                        <Form.Group className="mb-3" controlId="formBasicEmail">
                            <Form.Label>Username</Form.Label>
                            <Form.Control type="text" name="username" onChange={handleChange} className="input_field" required/>
                            {!userValid && <span className="valid_error">Invalid username.</span>}
                        </Form.Group>
                        <Row>
                            <Col>
                                <Form.Group className="mb-3" controlId="formBasicFirstName">
                                <Form.Label>First name</Form.Label>
                                <Form.Control type="text" name="first_name" onChange={handleChange} className="input_field" required/>
                                </Form.Group>
                            </Col>
                            <Col>
                                <Form.Group className="mb-3" controlId="formBasicLastName">
                                <Form.Label>Last name</Form.Label>
                                <Form.Control type="text" name="last_name" onChange={handleChange} className="input_field" required/>
                                </Form.Group>
                            </Col>
                        </Row>
                        <Form.Group className="mb-3" controlId="formBasicEmail">
                            <Form.Label>Email</Form.Label>
                            <Form.Control type="email" name="email" onChange={handleChange} className="input_field"/>
                        </Form.Group>
                        <Form.Group className="mb-3" controlId="formBasicPassword">
                            <Form.Label>Password</Form.Label>
                            <Form.Control type="password" name="password" onChange={handleChange} className="input_field" required/>
                            {!passValid && <span className="valid_error">It must contain at least one digit, lowercase, uppercase, special character and length between 6 and 20 characters.</span>}
                        </Form.Group>
                        <Form.Group className="mb-3" controlId="formBasicPassword">
                            <Form.Label>Confirm password</Form.Label>
                            <Form.Control type="password" name="confirm_password" onChange={handleChange} className="input_field" required/>
                            {!matchPassValid && <span className="valid_error">Password must be match.</span>}
                        </Form.Group>
                        <div className="d-grid gap-2">
                        <Button variant="primary" size="lg" className="main_button" type="submit">
                            Register
                        </Button>
                        </div>
                    </Form>
                </div>
            </div>
        </>
    )
}