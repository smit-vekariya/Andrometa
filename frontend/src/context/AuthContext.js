import { message } from 'antd';
import { jwtDecode } from "jwt-decode";
import React, { createContext, useCallback, useEffect, useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';

export const AuthContext = createContext();
const baseURL = process.env.REACT_APP_BASE_URL
export default function AuthProvider(){
    let navigate = useNavigate()
    let [authTokens, setAuthTokens] = useState(()=> localStorage.getItem("authTokens") ? JSON.parse(localStorage.getItem("authTokens")):null)
    let [user, setUser] = useState(() => localStorage.getItem("access") ? jwtDecode(localStorage.getItem("access")):null)
    let [loading_, setLoading_] = useState(true)
    const [messageApi, contextHolder] = message.useMessage();

    let loginUser = async (values) => {
        let response = await fetch(`${baseURL}/account/admin_login/`,{
            method:"POST",
            headers:{
                'Content-Type':"application/json"
            },
            body:JSON.stringify({"email":values.email,"password":values.password})
        })
        let data = await response.json()
        if (data.status === 1){
            setAuthTokens(data.data[0])
            setUser(jwtDecode(data.data[0]["access"]))
            localStorage.setItem("authTokens", JSON.stringify(data.data[0]))
            localStorage.setItem("access", data.data[0]["access"])
            navigate("/")
        }else{
            messageApi.open({type: 'error',content: data.message,});
        }
    }

    let logoutUser = useCallback((e) =>{
        setAuthTokens(null)
        setUser(null)
        localStorage.removeItem("authTokens")
        localStorage.removeItem("access")
        localStorage.removeItem("main_menu")
        navigate("/login")
    },[navigate])

    useEffect(()=>{
        if(authTokens && authTokens.status !== 0){
            setUser(jwtDecode(authTokens.access))
        }
        setLoading_(false)
    }, [authTokens, loading_])

    let contextData={
        "loginUser":loginUser,
        "logoutUser":logoutUser,
        "user":user,
        authTokens:authTokens,
        setUser:setUser,
        setAuthTokens:setAuthTokens,
        messageApi:messageApi,
    }
    return(
        <>
        {contextHolder}
        <AuthContext.Provider value={contextData}>
            {loading_ ? null:<Outlet  />}
            {/* <Outlet  /> */}
        </AuthContext.Provider>
        </>
    )
}