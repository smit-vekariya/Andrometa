import React, { useCallback, useEffect, useRef, useContext, useState } from "react"
import {Form, Input, Select, Checkbox, DatePicker, InputNumber, Button } from "antd"
import useAxios from "../../utils/useAxios"
import { AuthContext } from "../../context/AuthContext";
import dayjs from 'dayjs';


export default function TaskForm(prop){
    const api = useRef(useAxios())
    const id = prop.id
    const {messageApi} = useContext(AuthContext)
    const initialValues = {"clocked":[],"crontab":[],"interval":[],"solar":[],"task":[]} 
    const [preData, setPreData] = useState(initialValues)
    const data_initial = {
        "id": null,
        "name": "",
        "task": "",
        "enabled": false,
        "start_time": null,
        "last_run_at": null,
        "total_run_count": 0,
        "date_changed": "",
        "scheduler":"",
        "interval": "",
        "crontab": "",
        "clocked":"",
        "description":"",
        "one_off":false,
        "args":"",
        "kwargs":"",
        "expire_seconds":"",
        "expire_date":""
        
    }
    const [taskData, setTaskData] = useState(data_initial)

    const getTaskData = useCallback(async(id) =>{
        await api.current.get(`/manager/periodic_task/?id=${id}`)
        .then((res)=>{
            const data = res.data.data
            var new_data = {...data, "interval":data.scheduler_type === "interval" ? data.scheduler_id :"", "crontab":data.scheduler_type === "crontab" ? data.scheduler_id :"", "clocked":data.scheduler_type === "clocked" ? data.scheduler_id :"", "expire_date": data.expires ? (data.expires).includes("seconds") ? "": data.expires :""}
            delete new_data["expires"]
            setTaskData(new_data)
        })
        .catch((error)=>{
            messageApi.open({type: 'error', content:error.message})
        })

    },[setTaskData, messageApi])

    const getPreData = useCallback(async() =>{
        await api.current.get('/manager/task_pre_data/')
        .then((res)=>{
            var data = res.data.data[0]
            setPreData({"clocked":data.clocked,"crontab":data.crontab,"interval":data.interval,"solar":data.solar,"task":data.register_task})
            getTaskData(id)
        })
        .catch((error)=>{
            messageApi.open({type: 'error', content:error.message})
        })
    },[getTaskData, messageApi, id])

    useEffect(()=>{
        getPreData()
    },[getPreData])

    const saveForm = useCallback(async() =>{
        await api.current.post(`/manager/periodic_task/?periodic_id=${id}`, taskData)
        .then((res)=>{
            prop.getTaskList()
            messageApi.open({type: res.data.status === 0 ? 'error':'success', content:res.data.message})         
        })
        .catch((error)=>{
            messageApi.open({type: 'error', content:error.message})
        })
    },[taskData, messageApi, id, prop])

    return (
    <div>
        <Form id="taskForm" labelCol={{flex: '160px',}} labelWrap labelAlign="left" style={{maxWidth: 800,}} onFinish={saveForm}>
            <Form.Item  label="Name"  rules={[{required: true, message: 'Name is required'}]}>
                <Input value={taskData.name} onChange={(e) => setTaskData({...taskData, name:e.target.value})}/>
            </Form.Item>
            <Form.Item label="Task (registered)">
                <Select value={taskData.task} onChange={(value)=> setTaskData({...taskData, task:value})}>
                    {preData.task && preData.task.map((item, index)=>
                        <Select.Option key={index} value={item}>{item}</Select.Option>
                    )}
                </Select>
            </Form.Item>
            {/* <Form.Item  label="Task (custom)">
                <Input/>
            </Form.Item> */}
            <Form.Item label="Enabled" extra="Set to False to disable the schedule">
                <Checkbox checked={taskData.enabled} onChange={(e)=>setTaskData({...taskData, enabled:e.target.checked})}></Checkbox>
            </Form.Item>
            <Form.Item label="Description" extra="Detailed description about the details of this Periodic Task">
                <Input.TextArea rows={4} value={taskData.description} onChange={(e)=>setTaskData({...taskData, description:e.target.value})}/>
            </Form.Item>

            <div><b>Schedule</b></div><br></br>

            <Form.Item label="Interval Schedule" extra="Interval Schedule to run the task on. Set only one schedule type, leave the others null.">
                <Select value={taskData.interval} onChange={(value)=> setTaskData({...taskData, interval:value})}>
                    <Select.Option value=""></Select.Option>
                    {preData.interval && preData.interval.map((item, index)=>
                        <Select.Option key={index} value={item.id}>{item.name}</Select.Option>
                    )}
                </Select>
            </Form.Item>
            <Form.Item label="Crontab Schedule" extra="Crontab Schedule to run the task on. Set only one schedule type, leave the others null.">
                <Select value={taskData.crontab} onChange={(value)=> setTaskData({...taskData, crontab:value})}>
                    <Select.Option value=""></Select.Option>
                    {preData.crontab && preData.crontab.map((item, index)=>
                        <Select.Option key={index} value={item.id}>{item.crontab}</Select.Option>
                    )}
                </Select>
            </Form.Item>
            <Form.Item label="Clocked Schedule" extra="Clocked Schedule to run the task on. Set only one schedule type, leave the others null.">
                    <Select value={taskData.clocked} onChange={(value)=> setTaskData({...taskData, clocked:value})}>
                        <Select.Option value=""></Select.Option>
                        {preData.clocked && preData.clocked.map((item, index)=>
                            <Select.Option key={index} value={item.id}>{item.clock}</Select.Option>
                        )}
                    </Select>
            </Form.Item>
            <Form.Item label="Start Datetime" extra="Datetime when the schedule should begin triggering the task to run.">
                <DatePicker
                    showTime
                    value={taskData.start_time ? dayjs(taskData.start_time, 'YYYY-MM-DD HH:mm:ss'):""}
                    onChange={(value, dateString) => { setTaskData({...taskData, start_time:value})}}
                />
            </Form.Item>
            <Form.Item label="One-off Task" extra="if True, the schedule will only run the task a single time">
                <Checkbox checked={taskData.one_off} onChange={(e)=>setTaskData({...taskData, one_off:e.target.checked})}></Checkbox>
            </Form.Item>

            <div><b>Arguments</b></div><br></br>

            <Form.Item label="Positional Arguments" extra='JSON encoded positional arguments (Example: ["arg1", "arg2"])'>
                <Input.TextArea rows={4} value={taskData.args} onChange={(e)=>setTaskData({...taskData, args:e.target.value})}/>
            </Form.Item>
            <Form.Item label="Keyword Arguments" extra='JSON encoded keyword arguments (Example: {"argument": "value"})'>
                <Input.TextArea rows={4} value={taskData.kwargs} onChange={(e)=>setTaskData({...taskData, kwargs:e.target.value})}/>
            </Form.Item>

            <div><b>Execution Options</b></div><br></br>

            <Form.Item label="Expires Datetime">
                <DatePicker
                    showTime
                    value={taskData.expire_date ? dayjs(taskData.expire_date, 'YYYY-MM-DD HH:mm:ss'):""}
                    onChange={(value, dateString) => { setTaskData({...taskData, expire_date:value})}}
                />
            </Form.Item>
            <Form.Item label="Expires timedelta with seconds">
                <InputNumber value={taskData.expire_seconds} onChange={(value)=> setTaskData({...taskData, expire_seconds:value})}/>
            </Form.Item>

            <Form.Item>
                <Button type="primary" htmlType="submit">
                    Submit
                </Button>
            </Form.Item>
       </Form>
    </div>
    )
}