from django.contrib import admin
from django.urls import path, include
from . import views as v
urlpatterns = [
    path('api/search', v.search, name="search"),
    path('api/date', v.getDate, name="getDate"),
    path('api/addNewTask', v.addNewTask, name="addNewTask"),
    path('api/addduplicatetask', v.addduplicatetask, name="addduplicatetask"),
    path('api/AddContinuetask', v.AddContinuetask, name="AddContinuetask"),
    path('api/gettaskdetail', v.gettaskdetail, name="gettaskdetail"),


    path('api/deleteTask', v.deleteTask, name="deleteTask"),
    path('api/updateTask', v.updateTask, name="updateTask"),
    path('api/updateTaskZone',v.updateTaskZone, name='updateTaskZone'), #not using this coz multiple api 

    path('api/updateTaskZoneMultiple',v.updateTaskZoneMultiple, name='updateTaskZoneMultiple'),
    path('api/getTaskByDate', v.getTaskByDate, name="getTaskByDate"),
    path('api/zoneList', v.zoneList, name="zoneList"),
    path('api/yearList', v.yearList, name="yearList"),
    path('api/weekList', v.weekList, name="weekList"),
    path('api/userWeekList', v.userWeekList, name="userWeekList"),
    path('api/managertaskWeekList', v.managertaskWeekList, name="managertaskWeekList"),
    path('api/user_pending_task', v.user_pending_task, name="user_pending_task"),


    path('api/taskListApi', v.taskListApi, name="taskListApi"),
    

    path('api/GetAllTaskData', v.GetAllTaskData.as_view(), name="GetAllTaskData"),
    path('api/GetUserTaskData', v.GetUserTaskData.as_view(), name="GetUserTaskData"),
    path('api/Mytrackproscoredata',v.Mytrackproscoredata.as_view(),name="Mytrackproscoredata" ),
    path('api/assignUserTask', v.assignUserTask, name="assignUserTask"),
    path('api/ThreeParamTaskData',v.ThreeParamTaskData ,name="ThreeParamTaskData"),#done

    #Change status of task
    path('api/holdTaskStatus', v.holdTaskStatus, name="holdTaskStatus"),
    path('api/resumeTaskStatus', v.resumeTaskStatus, name="resumeTaskStatus"),
    path('api/closeTaskStatus',v.closeTaskStatus ,name="closeTaskStatus"),

    #cronejob
    path('api/cronejob',v.cronejob ,name="cronejob"),
    path('api/weeklycronejob',v.weeklycronejob ,name="weeklycronejob"),
    path('api/task_cordinator',v.get_task_coordiantor ,name="get_task_coordiantor"),
    path('api/get_employeetask',v.get_employeetask ,name="get_employeetask"),
    path('api/get_employeemanager',v.get_employeemanager ,name="get_employeemanager"),

    #notification
    path('api/addnotificationtype',v.add_notification_type ,name="addnotificationtype"),
    path('api/addnotification',v.add_notification ,name="addnotification"),
    path('api/notificationlist',v.notificationlist ,name="notificationlist"),
    path('api/leavenotificationlist',v.leavenotificationlist ,name="leavenotificationlist"),
    path('api/readnotifications',v.readnotifications ,name="readnotifications"),


#NEW
    path('api/gettaskbyid/<int:id>', v.gettaskbyid, name="gettaskbyid"),
    path('api/checktaskbymanager', v.checktaskbymanager, name="checktaskbymanager"),
    path('api/addNewTaskbyManager', v.addNewTaskbyManager, name="addNewTaskbyManager"),
    path('api/getTaskBymanagerDate', v.getTaskBymanagerDate, name="getTaskBymanagerDate"),

    path('api/Zonestatusbymanagerapi', v.Zonestatusbymanagerapi, name="Zonestatusbymanagerapi"),
    path('api/taskbonusbymanagerapi', v.taskbonusbymanagerapi, name="taskbonusbymanagerapi"),
    path('api/GetmanagerTaskData', v.GetmanagerTaskData.as_view(), name="GetmanagerTaskData"),
    path('api/managerWeekList', v.managerWeekList, name="managerWeekList"),
    
    path('api/employeetaskinfo', v.employeetaskinfo, name="employeetaskinfo"),
    path('api/Managertaskinfomapi', v.Managertaskinfomapi, name="Managertaskinfomapi"),
    path('api/Allemp_finalsubmit', v.Allemp_finalsubmit, name="Allemp_finalsubmit"),

    

    path('api/employeereviewinfo', v.employeereviewinfo, name="employeereviewinfo"),
    path('api/employeetasklistreviewinfo', v.employeetasklistreviewinfo, name="employeetasklistreviewinfo"),
    path('api/weeklydataapi', v.weeklydataapi, name="weeklydataapi"),
    path('api/userweekmodaldata', v.userweekmodaldata, name="userweekmodaldata"),
    path('api/tasktime', v.tasktime, name="tasktime"),
    path('api/weekdatesapi', v.weekdatesapi, name="weekdatesapi"),

    path('api/m_weeklyperc', v.m_weeklyperc, name="m_weeklyperc"),
    path('api/Empweeklytrackpro', v.Empweeklytrackpro, name="Empweeklytrackpro"),

    path('api/weekListbtn', v.weekListbtn, name="weekListbtn"),
    path('api/getweeklyempinfoapi', v.getweeklyempinfoapi, name="getweeklyempinfoapi"),
    path('api/viewweeklyempinfoapi', v.viewweeklyempinfoapi, name="viewweeklyempinfoapi"),
    path('api/publishdeptwiserankapi', v.publishdeptwiserankapi, name="publishdeptwiserankapi"),
    path('api/overall_week_avg_ny_dept_api', v.overall_week_avg_ny_dept_api, name="overall_week_avg_ny_dept_api"),

    path('api/completeweeklycronejob', v.completeweeklycronejob, name="completeweeklycronejob"),
    path('api/weeklytasks', v.weeklytasks, name="weeklytasks"),
    path('api/manager_remark', v.manager_remark, name="manager_remark"),
    path('api/employee_remark', v.employee_remark, name="employee_remark"),
    path('api/task_remark_list', v.task_remark_list, name="task_remark_list"),
    path('api/dashboardtask_remark_list', v.dashboardtask_remark_list, name="dashboardtask_remark_list"),    
    path('api/search_tasks', v.search_tasks, name="search_tasks"),


]