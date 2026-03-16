import { Button, Card, Col, Form, Input, Row } from 'antd';
import React, { useCallback, useContext, useEffect, useRef, useState } from "react";
import { AuthContext } from "../../context/AuthContext";
import useAxios from "../../utils/useAxios";
import '../component.css';



export default function Profile(){
    const api = useRef(useAxios())
    const [profile, setProfile] = useState({})
    const {messageApi} = useContext(AuthContext)
    const [disabled, setDisabled] = useState(true)
    const [profileImage, setProfileImage] = useState(null);
    const [previewImage, setPreviewImage] = useState(null);

    const getProfileData = useCallback(async() =>{
        await api.current.get('/account/user_profile/')
        .then((res)=>{
            if(res.data.status === 1){
                setProfile(res.data.data[0][0])
            }
            else{
                messageApi.open({type: 'error',content: res.data.message})
            }
        })
        .catch((error)=>{
            messageApi.open({type: 'error',content: error.message})
        })
    },[messageApi])

    useEffect(()=>{
        getProfileData()
    },[getProfileData])

    const editProfile=(e)=>{
        setProfile({...profile,[e.target.name]:e.target.value})
    }
    const saveProfile = async() =>{
        const formData = new FormData();
        for (const key in profile) {
            if (key !== 'profile') {
                formData.append(key, profile[key]);
            }
        }

        if (profileImage) {
            formData.append("file", profileImage, "profile.jpg");
        }

        await api.current.put(`/account/edit_profile/${profile.id}`,formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }})
            .then((res)=>{
                if(res.data.status ===1){
                    setDisabled(true)
                    messageApi.open({type: 'success',content: res.data.message})
                }
                else{
                    messageApi.open({type: 'error',content: res.data.message})
                }
            })
            .catch((error)=>{
                messageApi.open({type: 'error',content: error.message})
            })
    }

    const profileUpload = (e) =>{
        const file = e.target.files[0];
        setProfileImage(file)
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setPreviewImage(reader.result)
            };
            reader.readAsDataURL(file);
        }
    }
     return (
        <>
        <div className='title_tab'>
            <div className='title_tab_title'>Profile</div>
        </div>
        <div className='main_tab' style={{display:"flex"}}>
            <div style={{margin:"20px"}}>
                <Card style={{ width: 240 }} className="profile_card" cover={<img alt="profile" src={previewImage || profile.profile_path} />}>
                    <input type="file" id="profile" disabled={disabled}  accept="image/*" name="profile_name" onChange={profileUpload}/>
                </Card>
            </div>
            <div>
                <Form  style={{ maxWidth: 600,margin: '19px 6px'}}  layout="vertical" labelAlign="left">
                    <Row gutter={24}>
                        <Col span={12}>
                            <Form.Item label="Email (username)">
                                <Input type='email' className='edit' name ="email" onChange={editProfile} value={profile.email} disabled={disabled}></Input>
                            </Form.Item>
                        </Col>
                    </Row>
                    <Row gutter={24}>
                        <Col span={12}>
                            <Form.Item label="First Name">
                                <Input type='text' className='edit' name="first_name" onChange={editProfile} value={profile.first_name} disabled={disabled}></Input>
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item label="Last Name">
                                <Input type='text' className='edit' name="last_name" onChange={editProfile} value={profile.last_name} disabled={disabled}></Input>
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item label="Mobile No.">
                                <Input type='text' className='edit' name ="mobile" onChange={editProfile} value={profile.mobile} disabled={disabled}></Input>
                            </Form.Item>
                        </Col>
                         <Col span={12}>
                            <Form.Item label="Group">
                                <Input type='text' name ="mobile" value={profile.group__name} disabled></Input>
                            </Form.Item>
                        </Col>
                    </Row>
                </Form>
                <div>
                    {disabled ?
                    <Button type="primary" onClick={()=>setDisabled(false) }>Edit Profile</Button>
                    : <><Button type="primary" onClick={saveProfile}>Save Profile</Button>&nbsp;<Button onClick={()=>setDisabled(true) }>Cancel</Button></>}
                </div>
            </div>
        </div>
        </>
    )
}