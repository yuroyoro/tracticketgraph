<?cs include "header.cs"?>
<?cs include "macros.cs"?>

<link type="text/css" href="<?cs var:chrome.href ?>/tc/ticketgraph.css" rel="stylesheet"/>
<script language="JavaScript" src="<?cs var:chrome.href ?>/tc/FusionChartsFree/JSClass/FusionCharts.js"></script>
<head>

<body>

<div id="ticket-graph-main">
<form>
<div id="input-form">
	<table width="98%" border="0" cellspacing="0" cellpadding="3" align="left">
		<tr>
			<td>from &nbsp;<input id="current" name="current" type="text" size="14" maxlength="10" value="<?cs var:current ?>"/> <input id="size" name="size" type="text" size="4" maxlength="4" value="<?cs var:size ?>"/>&nbsp; days ago &nbsp; <input type="submit" value="update" /></td>
		</tr>
	</table>
</div>
<br/>
<div class="ticket-graph">
	<div class="chart">
		<h2>Ticket Count Timeline </h2>
		<table  width="98%" border="0" cellspacing="0" cellpadding="3" align="left">
			<tr> 
		    	<td valign="top" height="470px" align="center">
					<div id="count_chart_div"  align="center"> Ticket Count Timeline Chart . </div>
					<script type="text/javascript">
						var chart = new FusionCharts("<?cs var:chrome.href ?>/tc/FusionChartsFree/Charts/FCF_MSColumn2DLineDY.swf", "ChartId", "700", "450");
						chart.setDataXML("<?cs var:count_xml_data ?>");
						chart.render("count_chart_div");
					</script>
				</td>
			</tr>
			<tr>
				<td>
				<?cs each:table = count_table_data ?>
				<div class="data-table">
					<table cellpadding="0" cellspacing="1">
						<tr>
							<td class="header-date">Date</td>
							<?cs each:val = table.0 ?>
							<td class="col-date"><?cs var:val ?></td>
							<?cs /each ?>
						</tr>
						<tr>
							<td class="header-total">Total</td>
							<?cs each:val = table.1 ?>
							<td class="col-total"><?cs var:val ?></td>
							<?cs /each ?>
						</tr>
						<tr>
							<td class="header-opened">Opened</td>
							<?cs each:val = table.2 ?>
							<td class="col-opened"><?cs var:val ?></td>
							<?cs /each ?>
						</tr>
						<tr>
							<td class="header-added">Added</td>
							<?cs each:val = table.3 ?>
							<td class="col-added"><?cs var:val ?></td>
							<?cs /each ?>
						</tr>
						<tr>
							<td class="header-closed">Closed</td>
							<?cs each:val = table.4 ?>
							<td class="col-closed"><?cs var:val ?></td>
							<?cs /each ?>
						</tr>
					</table>
				</div>
				<?cs /each ?>
				</td>
			<tr>
		</table>
		<br/>
	</div>
	<div class="chart">
		<h2>Ticket Status Timeline </h2>
		<table width="98%" border="0" cellspacing="0" cellpadding="3" align="left">
			<tr> 
				<td valign="top" class="text" align="center">
					<div id="status_chart_div" class="chart_div" align="center"> Ticket Status Timeline Chart. </div>
					<script type="text/javascript">
						var chart = new FusionCharts("<?cs var:chrome.href ?>/tc/FusionChartsFree/Charts/FCF_StackedColumn2D.swf", "ChartId", "700", "450");
						chart.setDataXML("<?cs var:status_xml_data ?>");
						chart.render("status_chart_div");
					</script>
				</td>
			</tr>
			<tr>
				<td>
				<?cs each:table = status_table_data ?>
				<div class="data-table">
					<table cellpadding="0" cellspacing="1">
						<tr>
							<td class="header-date">Date</td>
							<?cs each:val = table.0 ?>
							<td class="col-date"><?cs var:val ?></td>
							<?cs /each ?>
						</tr>
						<tr>
							<td class="header-total">Total</td>
							<?cs each:val = table.1 ?>
							<td class="col-total"><?cs var:val ?></td>
							<?cs /each ?>
						</tr>
						<tr>
							<td class="header-opened">Opened</td>
							<?cs each:val = table.2 ?>
							<td class="col-opened"><?cs var:val ?></td>
							<?cs /each ?>
						</tr>
						<tr>
							<td class="header-new">New</td>
							<?cs each:val = table.3 ?>
							<td class="col-new"><?cs var:val ?></td>
							<?cs /each ?>
						</tr>
						<tr>
							<td class="header-assigned">Assigned</td>
							<?cs each:val = table.4 ?>
							<td class="col-assigned"><?cs var:val ?></td>
							<?cs /each ?>
						</tr>
						<tr>
							<td class="header-reopened">Reopened</td>
							<?cs each:val = table.5 ?>
							<td class="col-reopened"><?cs var:val ?></td>
							<?cs /each ?>
						</tr>
						<tr>
							<td class="header-closed">Closed</td>
							<?cs each:val = table.6 ?>
							<td class="col-closed"><?cs var:val ?></td>
							<?cs /each ?>
						</tr>
					</table>
				</div>
				<?cs /each ?>
				</td>
			</tr>
		</table>
	</div>
</div>
</form>
</div>
<?cs include "footer.cs"?>