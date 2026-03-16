import React, { useCallback, useContext, useEffect, useRef, useState } from "react";
import { AuthContext } from '../../context/AuthContext';
import useAxios from "../../utils/useAxios";
import { Card, Col,Checkbox, Button } from 'antd';
import "../component.css";


export default function Permissions(){
    const api = useRef(useAxios())
    const {messageApi} = useContext(AuthContext)
    const [permissions ,setPermission] = useState([])
    const [groupId ,setGroupId] = useState(0)
    const [groups, setGroups] = useState([])

    const getPermissions = useCallback(async(group_id) =>{
        setGroupId(group_id)
        await api.current.get(`/manager/group_permission/`,
            {params: {
                group_id:group_id
            }})
            .then((res) =>{
                setPermission(res.data.data)
            })
            .catch((error)=>{
                messageApi.open({type: 'error',content: error.message})
            })
    },[messageApi])
    
    const getGroup = useCallback(async()=>{
        await api.current.get('/manager/group_permission/')
        .then((res)=>{
            setGroups(res.data.data)
            getPermissions(res.data.data[0].id)
        }).catch((error)=>{
            messageApi.open({type: 'error',content: error.message})
        })
    },[messageApi,getPermissions])

  

    const setPerm = (pageIndex, permIndex) =>{
        const updatedPermissions = [...permissions];
        updatedPermissions[pageIndex].permission[permIndex].has_perm = !updatedPermissions[pageIndex].permission[permIndex].has_perm;
        setPermission(updatedPermissions)
    }

    const savePermissions = useCallback(async()  => {
        await api.current.post(`/manager/group_permission/`,{"group_id":groupId, "data":permissions})
        .then((res) =>{
            if(res.data.status === 1){
                messageApi.open({type: 'success',content: res.data.message})
            }else{
                messageApi.open({type: 'error',content: res.data.message})
            }
        })
        .catch((error)=>{
            messageApi.open({type: 'error',content: error.message})
        })
    },[groupId, permissions, messageApi])


    useEffect(()=>{
        getGroup();
    }, [getGroup])

    return (
        <>
            <div className='title_tab'>
                <div className='title_tab_title'>Permissions</div>
                <div className="title_tab_div">
                    <Button type="primary" onClick={savePermissions}>Save</Button>
                </div>
            </div>
            <div className='report_tab'>
                <div>
                    <label>Select Group &nbsp;
                        <select name="balance" id="select_value" onChange={(e)=>getPermissions(e.target.value)}>
                            {groups.map((data)=>(
                                <option key={data.id} value={data.id}>{data.name}</option>
                            ))}
                        </select>
                    </label>     
                </div>
            </div>
            <div className='main_tab perm_card'>
                {permissions.map((page, pageIndex) => (
                    <React.Fragment key={pageIndex}>
                        <Col span={8} >
                            <Card title={page.name}  bordered={false}>
                                {page.permission.map((perm, permIndex) => (
                                    <Checkbox  key={permIndex} onChange={() => setPerm(pageIndex, permIndex)} checked={perm.has_perm}>{perm.act_name}</Checkbox>
                                ))}
                            </Card>
                            <br></br>
                        </Col>                        
                    </React.Fragment>
                ))}
            </div>
        </>
    );
}