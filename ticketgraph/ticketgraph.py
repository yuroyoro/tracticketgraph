# TicketGraph plugin
import re , time
from datetime import date ,timedelta ,datetime
 
from trac.core import *
from trac.web.chrome import INavigationContributor ,ITemplateProvider
from trac.web.main import IRequestHandler
from trac.util import escape, Markup

class TicketGraphPlugin(Component):
    implements(INavigationContributor, IRequestHandler ,ITemplateProvider)

    # INavigationContributor methods
    def get_active_navigation_item(self, req):
        return 'ticketgraph'

    def get_navigation_items(self, req):
        yield 'mainnav', 'ticketgraph', Markup('<a href="%s">Ticket Graph</a>',
                self.env.href.ticketgraph())

    # IRequestHandler methods
    def match_request(self, req):
        return re.match(r'/ticketgraph(?:_trac)?(?:/.*)?$', req.path_info)
    
    def get_templates_dirs(self):
        from pkg_resources import resource_filename
        return [resource_filename(__name__, 'templates')]

    def get_htdocs_dirs(self):
        from pkg_resources import resource_filename
        return [('tc', resource_filename(__name__, 'htdocs'))]

    def process_request(self, req):
        
        today = date.today()

        current = req.args.get('current') or today.strftime("%Y-%m-%d")
        size = req.args.get('size') or "30"
        try :
            size = int( size )
            if size > 90 :
                size = 90
            elif size < 1 :
                size = 1
                
        except ValueError:
            size = 30
        
        db = self.env.get_db_cnx()
        
        # search condition end date
        try:
            st=time.strptime(current,'%Y-%m-%d')
            end_date = datetime(st.tm_year, st.tm_mon, st.tm_mday)
        except ValueError:  
            end_date = today
        
        end_date_str = end_date.strftime("%Y-%m-%d")
        current= end_date_str

        # search condition start date 
        start_date = end_date - timedelta(days=(size -1 ))
        start_date_str = start_date.strftime("%Y-%m-%d")
        
        cursor = db.cursor()

        # get new ticket count before [size] days ago from current
        remains_new_ticket_cnt = self.get_remains_new_ticket_count( cursor, start_date_str)
            
        # get assigned , reopened and closed ticket count before [size] days ago from current
        remains_ticket_cnt = self.get_remains_ticket_count(  cursor,start_date_str)
      
        # get 'new' ticket count by date ,between [size] days from current to current        
        new_ticket = self.get_new_ticket_count( cursor,start_date_str , end_date_str )
        
        # get increased ticket count by date and status ,between [size] days from current to current
        increased_ticket = self.get_increased_ticket_count( cursor, start_date_str , end_date_str )
        
        # get decreased ticket count by date and status ,between [size] days from current to current
        decreased_ticket = self.get_decreased_ticket_count( cursor, start_date_str , end_date_str )
        
        # get added ticket count by date
        added_ticket = self.get_added_ticket_count( cursor,  start_date_str , end_date_str )
        
        # get closed count by date
        closed_ticket = self.get_closed_ticket_count(cursor, start_date_str, end_date_str)
        
        db.rollback()
        
        # processing output 
        # data for xml
        categories = "<categories>"
        count_opened_ticket_dataset  = "<dataset seriesName='Opened Ticket' color='AFD8F8' showValues='1' >"
        count_added_ticket_dataset    ="<dataset seriesName='Added Ticket' color='F0807F' showValues='1' parentYAxis='S'>"
        count_closed_ticket_dataset = "<dataset seriesName='Closed Ticket' color='FF8000' showValues='1' parentYAxis='S' >"

        status_new_ticket_dataset    ="<dataset seriesName='New Ticket' color='F0807F' showValues='1' parentYAxis='S'>"
        status_assigned_ticket_dataset    ="<dataset seriesName='Assigned Ticket' color='99EE99' showValues='1' parentYAxis='S'>"
        status_reopened_ticket_dataset    ="<dataset seriesName='Reopened Ticket' color='EEEE99' showValues='1' parentYAxis='S'>"
        status_closed_ticket_dataset = "<dataset seriesName='Closed Ticket' color='FF8000' showValues='1' parentYAxis='S' >"
        
        # data for table
        date_list                   = []
        count_total_ticket_list     = []
        count_opened_ticket_list    = []
        count_added_ticket_list     = []
        count_closed_ticket_list    = []
        
        status_total_ticket_list    = []
        status_opened_ticket_list   = []
        status_new_ticket_list      = []
        status_assigned_ticket_list = []
        status_reopened_ticket_list = []
        status_closed_ticket_list   = []
        
        max_cnt    = 0
        max_status = 0
        
        remains_assigned_ticket_cnt = remains_ticket_cnt[0]
        remains_reopened_ticket_cnt = remains_ticket_cnt[1]
        remains_closed_ticket_cnt = remains_ticket_cnt[2]
        
        opened_ticket_cnt = remains_new_ticket_cnt + remains_assigned_ticket_cnt + remains_reopened_ticket_cnt
        total_ticket_cnt  = opened_ticket_cnt + remains_closed_ticket_cnt
        
        for i in range(size ) :
            # increment date
            date_obj = start_date + timedelta(days=i)
            date_str = date_obj.strftime("%Y-%m-%d")
            
            # get delta ticket count by status 
            increased_new_ticket_cnt      = self.search_count_by_date(date_str, new_ticket) + self.search_count_by_date(date_str, increased_ticket ,1)
            increased_assigned_ticket_cnt = self.search_count_by_date(date_str, increased_ticket ,2)
            increased_reopened_ticket_cnt = self.search_count_by_date(date_str, increased_ticket ,3)
            increased_closed_ticket_cnt   = self.search_count_by_date(date_str, increased_ticket ,4)

            decreased_new_ticket_cnt      = self.search_count_by_date(date_str, decreased_ticket ,1)
            decreased_assigned_ticket_cnt = self.search_count_by_date(date_str, decreased_ticket ,2)
            decreased_reopened_ticket_cnt = self.search_count_by_date(date_str, decreased_ticket ,3)
            decreased_closed_ticket_cnt   = self.search_count_by_date(date_str, decreased_ticket ,4)
            
            diff_new_ticket_cnt      = increased_new_ticket_cnt - decreased_new_ticket_cnt
            diff_assigned_ticket_cnt = increased_assigned_ticket_cnt - decreased_assigned_ticket_cnt
            diff_reopened_ticket_cnt = increased_reopened_ticket_cnt - decreased_reopened_ticket_cnt
            diff_closed_ticket_cnt   = increased_closed_ticket_cnt - decreased_closed_ticket_cnt
        
            # calculate count by status 
            remains_new_ticket_cnt      += diff_new_ticket_cnt  
            remains_assigned_ticket_cnt += diff_assigned_ticket_cnt
            remains_reopened_ticket_cnt += diff_reopened_ticket_cnt
            remains_closed_ticket_cnt   += diff_closed_ticket_cnt
        
            opened_ticket_cnt = remains_new_ticket_cnt +  remains_assigned_ticket_cnt + remains_reopened_ticket_cnt
            total_ticket_cnt = opened_ticket_cnt + remains_closed_ticket_cnt
            
            added_ticket_cnt  = self.search_count_by_date(date_str, added_ticket)
            closed_ticket_cnt = self.search_count_by_date(date_str, closed_ticket)
             
            # create xml data
            categories += "    <category name='%s' /> " % date_str
            
            count_opened_ticket_dataset    += "    <set value='%d' /> "  % opened_ticket_cnt
            count_added_ticket_dataset     += "    <set value='%d' /> "  % added_ticket_cnt
            count_closed_ticket_dataset    += "    <set value='%d' /> "  % closed_ticket_cnt
    
            status_new_ticket_dataset      += "    <set value='%d' /> "  % remains_new_ticket_cnt
            status_assigned_ticket_dataset += "    <set value='%d' /> "  % remains_assigned_ticket_cnt
            status_reopened_ticket_dataset += "    <set value='%d' /> "  % remains_reopened_ticket_cnt
            status_closed_ticket_dataset   += "    <set value='%d' /> "  % remains_closed_ticket_cnt
        
            # create data for table 
            date_list.append( date_str )
            count_total_ticket_list.append( total_ticket_cnt )
            count_opened_ticket_list.append( opened_ticket_cnt )
            count_added_ticket_list.append( added_ticket_cnt )
            count_closed_ticket_list.append( closed_ticket_cnt )
            
            status_total_ticket_list.append( total_ticket_cnt )
            status_opened_ticket_list.append( opened_ticket_cnt )
            status_new_ticket_list.append( remains_new_ticket_cnt )
            status_assigned_ticket_list.append( remains_assigned_ticket_cnt )
            status_reopened_ticket_list.append( remains_reopened_ticket_cnt )
            status_closed_ticket_list.append( remains_closed_ticket_cnt )    
            
            # calculate max value for chart axis y
            if max_cnt < opened_ticket_cnt :
                max_cnt = opened_ticket_cnt
            if max_cnt < added_ticket_cnt:
                max_cnt = added_ticket_cnt
            if max_cnt < closed_ticket_cnt :
                max_cnt = closed_ticket_cnt
                
            if max_status < total_ticket_cnt :
                max_status = total_ticket_cnt            
            
        categories += "</categories>"
        count_opened_ticket_dataset    += "</dataset >"
        count_added_ticket_dataset     += "</dataset >"
        count_closed_ticket_dataset    += "</dataset >"
        
        status_new_ticket_dataset      += "</dataset >"
        status_assigned_ticket_dataset += "</dataset >"
        status_reopened_ticket_dataset += "</dataset >"
        status_closed_ticket_dataset   += "</dataset >"
        
        l = max_cnt / 50
        max_cnt = 50 * ( l + 1)
        l = max_status / 50
        max_status = 50 * ( l + 1)
        
        # build xml for chart
        count_xml_data = "<graph caption='Ticket Count Timeline Chart (from %s to %s )' PYAxisName='Opened Tickets' SYAxisName='Added or Closed Tickets' "  % (start_date_str , end_date_str )
        count_xml_data += "numberPrefix='' showvalues='1'  numDivLines='4' formatNumberScale='0' " 
        count_xml_data += "decimalPrecision='0' rotateNames='1'  " 
        count_xml_data += "anchorSides='10' anchorRadius='3' anchorBorderColor='999999' " 
        count_xml_data += "SYAxisMaxValue='%d' PYAxisMaxValue='%d'>" % ( max_cnt , max_cnt)
                  
        count_xml_data += categories
        count_xml_data += count_opened_ticket_dataset
        count_xml_data += count_added_ticket_dataset
        count_xml_data += count_closed_ticket_dataset
        count_xml_data += "</graph>"
        
        status_xml_data = "<graph caption='Ticket Status Timeline Chart (from %s to %s )' PYAxisName='Tickets' SYAxisName='Tickets' "  % (start_date_str , end_date_str )
        status_xml_data += "numberPrefix='' showvalues='1'  numDivLines='4' formatNumberScale='0' " 
        status_xml_data += "decimalPrecision='0' rotateNames='1'  " 
        status_xml_data += "anchorSides='10' anchorRadius='3' anchorBorderColor='999999' " 
        status_xml_data += "SYAxisMaxValue='%d' PYAxisMaxValue='%d'>" % ( max_cnt , max_cnt)
                  
        status_xml_data += categories
        status_xml_data += status_closed_ticket_dataset
        status_xml_data += status_new_ticket_dataset
        status_xml_data += status_assigned_ticket_dataset
        status_xml_data += status_reopened_ticket_dataset
        status_xml_data += "</graph>"
        
        # build data list for table
        count_table_data = []
        status_table_data = []
        table_cnt = ( size / 15 ) + 1
        for i in range(table_cnt) :
            from_idx = i * 15
            to_idx   = (i + 1) * 15
            if to_idx > size :
                to_idx = size
            
            sliced_date_list                   = date_list[from_idx:to_idx]                  
            sliced_count_total_ticket_list     = count_total_ticket_list[from_idx:to_idx]    
            sliced_count_opened_ticket_list    = count_opened_ticket_list[from_idx:to_idx]   
            sliced_count_added_ticket_list     = count_added_ticket_list[from_idx:to_idx]    
            sliced_count_closed_ticket_list    = count_closed_ticket_list[from_idx:to_idx]   
                               
            sliced_status_total_ticket_list    = status_total_ticket_list[from_idx:to_idx]   
            sliced_status_opened_ticket_list   = status_opened_ticket_list[from_idx:to_idx]  
            sliced_status_new_ticket_list      = status_new_ticket_list[from_idx:to_idx]     
            sliced_status_assigned_ticket_list = status_assigned_ticket_list[from_idx:to_idx]
            sliced_status_reopened_ticket_list = status_reopened_ticket_list[from_idx:to_idx]
            sliced_status_closed_ticket_list   = status_closed_ticket_list[from_idx:to_idx]
            
            count_table_data.append( (sliced_date_list, sliced_count_total_ticket_list,sliced_count_opened_ticket_list,sliced_count_added_ticket_list,sliced_count_closed_ticket_list))
            status_table_data.append( (sliced_date_list,sliced_status_total_ticket_list,sliced_status_opened_ticket_list,sliced_status_new_ticket_list,sliced_status_assigned_ticket_list,sliced_status_reopened_ticket_list,sliced_status_closed_ticket_list) )
        
        # send data xml ,size and current to template
        req.hdf.set_unescaped('current' , current)
        req.hdf.set_unescaped('size' , size )
        req.hdf.set_unescaped('count_xml_data' , count_xml_data )
        req.hdf.set_unescaped('status_xml_data' , status_xml_data )
        req.hdf.set_unescaped('count_table_data' , count_table_data )
        req.hdf.set_unescaped('status_table_data' , status_table_data )
        
        self.log.debug("[count_xml_data]")
        self.log.debug(count_xml_data)
        
        self.log.debug("[status_xml_data]")
        self.log.debug(status_xml_data)
        
        self.log.debug("[count_table_data]")
        self.log.debug(count_table_data)
        
        self.log.debug("[status_table_data]")
        self.log.debug(status_table_data)
        
        return 'ticketgraph.cs' , None 

    
    def get_remains_new_ticket_count(self , cursor, start_date_str):
        sql =   """
SELECT count(*) New
  FROM (
        SELECT id
          FROM ticket
         WHERE time < strftime('%%s','%s 23:59:59' ,'-1 day')
       ) t 
  LEFT OUTER JOIN 
       (
        SELECT tc1.id id, newvalue
         FROM (
               SELECT ticket id, time ,newvalue
                 FROM ticket_change 
                WHERE field='status' 
                  AND time < strftime('%%s','%s 23:59:59' ,'-1 day')
              ) tc1 
         JOIN (
               SELECT ticket id, max(time) last_change_time,min(time) first_change_time
                 FROM ticket_change 
                WHERE field='status' 
                  AND time < strftime('%%s','%s 23:59:59' ,'-1 day')
                GROUP BY id 
              ) tc2
          ON tc1.id = tc2.id AND tc1.time = tc2.last_change_time
       ) tc ON t.id = tc.id 
 WHERE tc.newvalue IS NULL OR tc.newvalue = 'new'
        """ 
        sql = sql % ( start_date_str  ,start_date_str,start_date_str)
        
        self.log.debug("[get_remains_new_ticket_count]")
        self.log.debug( sql )
        cursor.execute( sql )  
        
        cnt = 0
        rec = cursor.fetchone() 
        if rec != None and rec[0] != None :
            cnt = rec[0]
        return cnt
    
    def get_remains_ticket_count(self , cursor, start_date_str):
        sql =   """
SELECT ifnull( sum( Assigned) ,0 ) Assigned ,
       ifnull( sum( Reopened) ,0 ) Reopened ,
       ifnull( sum( Closed) ,0 )   Closed 
  FROM (
        SELECT ticket id, date(time ,'unixepoch')tm ,time,
               (CASE newvalue WHEN 'assigned' THEN 1 ELSE 0 END) Assigned,
               (CASE newvalue WHEN 'reopened' THEN 1 ELSE 0 END) Reopened,
               (CASE newvalue WHEN 'closed' THEN 1 ELSE 0 END) Closed
          FROM ticket_change 
         WHERE field='status' 
           AND time <= strftime('%%s','%s 23:59:59' ,'-1 day')
       ) tc1 
  JOIN (
        SELECT ticket id, max(time) last_change_time,min(time) first_change_time
          FROM ticket_change 
         WHERE field='status' 
           AND time <= strftime('%%s','%s 23:59:59' ,'-1 day')
         GROUP BY id 
       ) tc2
   ON tc1.id = tc2.id AND tc1.time = tc2.last_change_time
        """ 
        sql = sql % ( start_date_str ,start_date_str  )
        
        self.log.debug("[get_remains_ticket_count]")
        self.log.debug( sql )
        cursor.execute( sql )  
        
        return cursor.fetchone() or []
    
    def get_new_ticket_count(self ,cursor, start_date_str ,end_date_str):
        sql = """  
SELECT ifnull( tc.tm , t.tm) dt, count(*) New
  FROM (
        SELECT date(time,'unixepoch') tm, id
          FROM ticket
         WHERE time <= strftime('%%s','%s 23:59:59')
       ) t 
  LEFT JOIN 
       (
        SELECT tc1.id id ,tc1.tm tm, newvalue
         FROM (
               SELECT ticket id, date(time ,'unixepoch')tm ,time ,newvalue
                 FROM ticket_change 
                WHERE field='status' 
                  AND time >= strftime('%%s','%s') AND time <= strftime('%%s','%s 23:59:59')
              ) tc1 
         JOIN (
               SELECT ticket id, date(time ,'unixepoch')tm ,max(time) last_change_time,min(time) first_change_time
                 FROM ticket_change 
                WHERE field='status' 
                  AND time >= strftime('%%s','%s') AND time <= strftime('%%s','%s 23:59:59')
                GROUP BY tm , id 
              ) tc2
          ON tc1.id = tc2.id AND tc1.time = tc2.last_change_time
       ) tc 
    ON t.id = tc.id 
   AND t.tm = tc.tm
 WHERE tc.newvalue IS NULL OR tc.newvalue = 'new'
 GROUP BY dt
 HAVING dt >= '%s'
 ORDER BY dt  ASC
        """         
        sql = sql % ( end_date_str ,start_date_str ,end_date_str ,start_date_str ,end_date_str,start_date_str )
        
        self.log.debug("[get_new_ticket_count]")
        self.log.debug( sql )
        cursor.execute( sql )
        
        return cursor.fetchall() or []
    
    def get_increased_ticket_count(self ,cursor, start_date_str ,end_date_str):
        sql = """  
SELECT tc.tm tm ,
       ifnull(sum( New) ,0 ) New ,
       ifnull(sum( Assigned) ,0 ) Assigned ,
       ifnull(sum( Reopened) ,0 ) Reopened ,
       ifnull(sum( Closed) ,0  )  Closed 
  FROM (
       (
        SELECT tc1.id id,tc1.tm tm, oldvalue
         FROM (
               SELECT ticket id, date(time ,'unixepoch')tm ,time ,oldvalue
                 FROM ticket_change 
                WHERE field='status' 
                  AND time >= strftime('%%s','%s') AND time <= strftime('%%s','%s 23:59:59')
               ORDER BY tm , id
              ) tc1 
         JOIN (
               SELECT ticket id, date(time ,'unixepoch') tm ,max(time) last_change_time,min(time) first_change_time
                 FROM ticket_change 
                WHERE field='status' 
                  AND time >= strftime('%%s','%s') AND time <= strftime('%%s','%s 23:59:59')
                GROUP BY tm , id 
                ORDER BY tm , id
              ) tc2
          ON tc1.id = tc2.id AND tc1.time = tc2.first_change_time
       ) tc_first
       JOIN 
       (
        SELECT tc3.id id,tc3.tm tm, newvalue,
               (CASE newvalue WHEN 'new' THEN 1 ELSE 0 END)      New,
               (CASE newvalue WHEN 'assigned' THEN 1 ELSE 0 END) Assigned,
               (CASE newvalue WHEN 'reopened' THEN 1 ELSE 0 END) Reopened,
               (CASE newvalue WHEN 'closed' THEN 1 ELSE 0 END)   Closed
         FROM (
               SELECT ticket id, date(time ,'unixepoch')tm ,time ,newvalue
                 FROM ticket_change 
                WHERE field='status' 
                  AND time >= strftime('%%s','%s') AND time <= strftime('%%s','%s 23:59:59')
               ORDER BY tm , id
              ) tc3 
         JOIN (
               SELECT ticket id, date(time ,'unixepoch')tm ,max(time) last_change_time,min(time) first_change_time
                 FROM ticket_change 
                WHERE field='status' 
                  AND time >= strftime('%%s','%s') AND time <= strftime('%%s','%s 23:59:59')
                GROUP BY tm , id 
                ORDER BY tm , id
              ) tc4
          ON tc3.id = tc4.id AND tc3.time = tc4.last_change_time
       ) tc_last 
    ON tc_first.id = tc_last.id 
   AND tc_first.tm = tc_last.tm 
   AND tc_first.oldvalue <> tc_last.newvalue
   ) tc
GROUP BY tm
ORDER BY tm ASC
        """         
        sql = sql % ( start_date_str ,end_date_str ,start_date_str ,end_date_str,start_date_str ,end_date_str ,start_date_str ,end_date_str)
        
        self.log.debug("[get_increased_ticket_count]")
        self.log.debug( sql )
        cursor.execute( sql )
        
        return cursor.fetchall() or []
    
    def get_decreased_ticket_count(self ,cursor, start_date_str ,end_date_str):
        sql = """  
SELECT tc.tm tm ,
       ifnull(sum(Diff_New) ,0 )      Diff_New,
       ifnull(sum(Diff_Assigned) ,0 ) Diff_Assigned,
       ifnull(sum(Diff_Reopened) ,0 ) Diff_Reopened,
       ifnull(sum(Diff_Closed) ,0 )   Diff_Closed
  FROM ticket t
  JOIN (
       (
        SELECT tc1.id id,tc1.tm tm, oldvalue,
               (CASE oldvalue WHEN 'new' THEN 1 ELSE 0 END)      Diff_New,
               (CASE oldvalue WHEN 'assigned' THEN 1 ELSE 0 END) Diff_Assigned,
               (CASE oldvalue WHEN 'reopened' THEN 1 ELSE 0 END) Diff_Reopened,
               (CASE oldvalue WHEN 'closed' THEN 1 ELSE 0 END)   Diff_Closed
         FROM (
               SELECT ticket id, date(time ,'unixepoch')tm ,time ,oldvalue
                 FROM ticket_change 
                WHERE field='status' 
                  AND time >= strftime('%%s','%s') AND time <= strftime('%%s','%s 23:59:59')
               ORDER BY tm , id
              ) tc1 
         JOIN (
               SELECT ticket id, date(time ,'unixepoch') tm ,max(time) last_change_time,min(time) first_change_time
                 FROM ticket_change 
                WHERE field='status' 
                  AND time >= strftime('%%s','%s') AND time <= strftime('%%s','%s 23:59:59')
                GROUP BY tm , id 
                ORDER BY tm , id
              ) tc2
          ON tc1.id = tc2.id AND tc1.time = tc2.first_change_time
       ) tc_first
       JOIN 
       (
        SELECT tc3.id id,tc3.tm tm, newvalue
         FROM (
               SELECT ticket id, date(time ,'unixepoch')tm ,time ,newvalue
                 FROM ticket_change 
                WHERE field='status' 
                  AND time >= strftime('%%s','%s') AND time <= strftime('%%s','%s 23:59:59')
               ORDER BY tm , id
              ) tc3 
         JOIN (
               SELECT ticket id, date(time ,'unixepoch')tm ,max(time) last_change_time,min(time) first_change_time
                 FROM ticket_change 
                WHERE field='status' 
                  AND time >= strftime('%%s','%s') AND time <= strftime('%%s','%s 23:59:59')
                GROUP BY tm , id 
                ORDER BY tm , id
              ) tc4
          ON tc3.id = tc4.id AND tc3.time = tc4.last_change_time
       ) tc_last 
    ON tc_first.id = tc_last.id 
   AND tc_first.tm = tc_last.tm 
   AND tc_first.oldvalue <> tc_last.newvalue
  ) tc
 ON t.id = tc.id AND date(t.time ,'unixepoch') <> tc.tm
GROUP by tm
HAVING tm >= '%s'
ORDER BY tm
        """         
        sql = sql % ( start_date_str ,end_date_str ,start_date_str ,end_date_str,start_date_str ,end_date_str,start_date_str ,end_date_str , start_date_str)
        
        self.log.debug("[get_decreased_ticket_count]")
        self.log.debug( sql )
        cursor.execute( sql )
        
        return cursor.fetchall() or []
           
    def get_added_ticket_count(self ,cursor, start_date_str ,end_date_str):
        sql = """  
SELECT date(time,'unixepoch') tm, count(*) as Count
  FROM ticket
 WHERE time >= strftime('%%s','%s') AND time <= strftime('%%s','%s 23:59:59')
 GROUP BY tm
 ORDER BY tm ASC
        """         
        sql = sql % ( start_date_str ,end_date_str )
        
        self.log.debug("[get_added_ticket_count]")
        self.log.debug( sql )
        cursor.execute( sql )
        
        return cursor.fetchall() or []

    def get_closed_ticket_count(self ,cursor, start_date_str ,end_date_str):
        sql = """  
SELECT date(time,'unixepoch') AS Closed, count(*) AS Count 
 FROM ticket_change 
WHERE field = 'status' AND newvalue = 'closed' 
  AND time >= strftime('%%s','%s') AND time <= strftime('%%s','%s 23:59:59')
GROUP BY Closed
ORDER BY Closed ASC
        """         
        sql = sql % ( start_date_str ,end_date_str )
        
        self.log.debug("[get_closed_ticket_count]")
        self.log.debug( sql )
        cursor.execute( sql )
        
        return cursor.fetchall() or []
                        
             
    def search_count_by_date(self , date_str , records , idx=1):
        for row in records :
            key = row[0]
            if date_str == key :
                return int( row[idx] )
        
        return 0
