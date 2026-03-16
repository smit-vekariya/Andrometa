import React, { useCallback, useEffect, useRef, useState, useContext } from "react";
import useAxios from "../../utils/useAxios";
import { AuthContext } from "../../context/AuthContext";
import { Card, Col, Button } from 'antd';
import TaskForm from '../js/TaskForm'



export default function TaskScheduler(){
    const api = useRef(useAxios())
    const {messageApi} = useContext(AuthContext)

    const [taskData, setTaskData] = useState([])
    const [taskResult, setTaskResult] = useState([])
    const [title, setTitle] = useState("")
    const [isEdit, setIsEdit] = useState(null)
    const [id, setId] = useState(0)

    const getTaskList = useCallback(async() =>{
        await api.current.get(`/manager/periodic_task/`)
        .then((res)=>{
            setTaskData(res.data.data)
        })
        .catch((error)=>{
            messageApi.open({type: 'error', content:error.message})
        })

    },[setTaskData, messageApi])

    const showResult = useCallback(async(name) =>{
        await api.current.get(`manager/periodic_task_result/?periodic_name=${name}`)
        .then((res)=>{
            setIsEdit(false)
            setTaskResult([])
            setTitle("Results : " + name)
            if(res.data.status === 1){
                setTaskResult(res.data.data)
            }
        })
    },[])

    const editTask = useCallback((id, name) => {
        setTitle("Edit : " + name)
        setId(id)
        setIsEdit(true)
    },[])


    useEffect(()=>{
        getTaskList()
    },[getTaskList])

    return(
        <>
            
            <div className='title_tab'>
                <div className='title_tab_title'>Task Scheduler</div>
            </div>
            <div className="main_tab main_tab_result">
                <div className="list_div">
                    {taskData.map((item) =>
                        <div key={item.id}>
                        <Col>
                            <Card title={item.name} bordered={false} >
                                <div style={{ whiteSpace: "pre-line" }}>
                                    <p>Task: {item.task}</p>
                                    <p>Expire: {item.expires}</p>
                                    <p>Start time: {item.start_time}</p>
                                    <p>Last run time: {item.last_run_at}</p>
                                    <p>Total run: {item.total_run_count}</p>
                                    <p>Date changed: {item.date_changed}</p>
                                    <p>Status: { item.enabled ? "Enabled" : "Disabled"}</p>
                                    <div>
                                        <Button onClick={()=> editTask(item.id, item.name)}>Edit</Button>&nbsp;
                                        <Button onClick={()=> showResult(item.name)}>Result</Button>&nbsp;
                                        <Button>Delete</Button>&nbsp;
                                        { item.enabled ?
                                            <Button>Disable</Button> : <Button>Enable</Button>
                                        } &nbsp;
                                    </div>
                                </div>
                            </Card>
                        </Col>
                        <br></br>
                        </div>
                    )}
                </div>
                {isEdit == null ? <div className="no_data">No Data</div>:
                    <div className="result_div">
                        <div className="title_div">
                            <h3>{title}</h3>
                        </div><br></br>
                        {isEdit ? 
                            <TaskForm id={id} getTaskList={getTaskList} ></TaskForm> :
                            <>
                                {taskResult.length > 0 ?
                                <div>
                                    <table style={{width:'100%'}}>
                                        <tbody>
                                            <tr>
                                                <th>Created Date</th>
                                                <th>Status</th>
                                                <th>Task Name</th>
                                                <th>Result</th>
                                            </tr>
                                            {taskResult.map((item) =>
                                                <tr  key={item.id}>
                                                    <td>{item.date_created}</td>
                                                    <td>{item.status}</td>
                                                    <td>{item.task_name}</td>
                                                    <td>{item.result}</td>
                                                </tr>
                                            )}
                                        </tbody>
                                    </table>
                                </div> : null} 
                            </> 
                        }
                    </div>
                }
            </div>
        </>
    )

}