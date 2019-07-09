import datetime
import io
import sys
import time
from xml.sax import saxutils


# ----------------------------------------------------------------------
# Template

class Template_mixin(object):
    HTML_TMPL = r"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "httpss://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="httpss://www.w3.org/1999/xhtml">
<head>
    <title>%(title)s</title>
    <meta httpss-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    %(stylesheet)s
</head>
<body>
<script language="javascript" type="text/javascript"><!--
output_list = Array();

/* level - 0:Summary; 1:Failed; 2:All */
function showCase(level) {
    trs = document.getElementsByTagName("tr");
    for (var i = 0; i < trs.length; i++) {
        tr = trs[i];
        id = tr.id;
        if (id.substr(0,2) == 'ft') {
            if (level < 1) {
                tr.className = 'hiddenRow';
            }
            else {
                tr.className = '';
            }
        }
        if (id.substr(0,2) == 'pt') {
            if (level > 1) {
                tr.className = '';
            }
            else {
                tr.className = 'hiddenRow';
            }
        }
    }
}


function showClassDetail(cid, count) {
    var id_list = Array(count);
    var toHide = 1;
    for (var i = 0; i < count; i++) {
        tid0 = 't' + cid.substr(1) + '.' + (i+1);
        tid = 'f' + tid0;
        tr = document.getElementById(tid);
        if (!tr) {
            tid = 'p' + tid0;
            tr = document.getElementById(tid);
        }
        id_list[i] = tid;
        if (tr.className) {
            toHide = 0;
        }
    }
    for (var i = 0; i < count; i++) {
        tid = id_list[i];
        if (toHide) {
            document.getElementById('div_'+tid).style.display = 'none'
            document.getElementById(tid).className = 'hiddenRow';
        }
        else {
            document.getElementById(tid).className = '';
        }
    }
}


function showTestDetail(div_id){
    var details_div = document.getElementById(div_id)
    var displayState = details_div.style.display
    // alert(displayState)
    if (displayState != 'block' ) {
        displayState = 'block'
        details_div.style.display = 'block'
    }
    else {
        details_div.style.display = 'none'
    }
}


function html_escape(s) {
    s = s.replace(/&/g,'&amp;');
    s = s.replace(/</g,'&lt;');
    s = s.replace(/>/g,'&gt;');
    return s;
}

/* obsoleted by detail in <div>
function showOutput(id, name) {
    var w = window.open("", //url
                    name,
                    "resizable,scrollbars,status,width=800,height=450");
    d = w.document;
    d.write("<pre>");
    d.write(html_escape(output_list[id]));
    d.write("\n");
    d.write("<a href='javascript:window.close()'>close</a>\n");
    d.write("</pre>\n");
    d.close();
}
*/
--></script>

%(heading)s
%(report)s
%(ending)s

</body>
</html>
"""
    # variables: (title, generator, stylesheet, heading, report, ending)

    # ------------------------------------------------------------------------
    # Stylesheet
    #
    # alternatively use a <link> for external style sheet, e.g.
    #   <link rel="stylesheet" href="$url" type="text/css">

    STYLESHEET_TMPL = """
<style type="text/css" media="screen">
body        { font-family: verdana, arial, helvetica, sans-serif; font-size: 80%; }
table       { font-size: 100%; }
pre         { }

/* -- heading ---------------------------------------------------------------------- */
h1 {
	font-size: 16pt;
	color: gray;
}
.heading {
    margin-top: 0ex;
    margin-bottom: 1ex;
}

.heading .attribute {
    margin-top: 1ex;
    margin-bottom: 0;
}

.heading .description {
    margin-top: 4ex;
    margin-bottom: 6ex;
}

/* -- css div popup ------------------------------------------------------------------------ */
a.popup_link {
}

a.popup_link:hover {
    color: red;
}

.popup_window {
    display: none;
    position: relative;
    left: 0px;
    top: 0px;
    /*border: solid #627173 1px; */
    padding: 10px;
    background-color: #E6E6D6;
    font-family: "Lucida Console", "Courier New", Courier, monospace;
    text-align: left;
    font-size: 8pt;
    width: 500px;
}

}
/* -- report ------------------------------------------------------------------------ */
#show_detail_line {
    margin-top: 3ex;
    margin-bottom: 1ex;
}
#result_table {
    width: 80%;
    border-collapse: collapse;
    border: 1px solid #777;
}
#header_row {
    font-weight: bold;
    color: white;
    background-color: #777;
    height:40px
}
#result_table td {
    border: 1px solid #777;
    padding: 2px;
}
#total_row  { font-weight: bold; }
.passCase   { color: #fff; font-weight: bold; background-color: rgb(17, 116, 91); height:40px;}
.failCase   { color: #fff; font-weight: bold; background-color: rgb(243, 151, 151); height:40px;}
.errorCase  { color: #fff; font-weight: bold; background-color: rgb(238, 77, 77); height:40px;}
.hiddenRow  { display: none; }
.testcase   { margin-left: 2em; }


/* -- ending ---------------------------------------------------------------------- */
#ending {
}

</style>
"""

    # ------------------------------------------------------------------------
    # Heading
    #

    HEADING_TMPL = """<div class='heading'>
<h1>%(title)s</h1>
%(parameters)s
<p class='description'>%(description)s</p>
</div>

"""  # variables: (title, parameters, description)

    HEADING_ATTRIBUTE_TMPL = """<p class='attribute'><strong>%(name)s:</strong> %(value)s</p>
"""  # variables: (name, value)

    # ------------------------------------------------------------------------
    # Report
    #

    REPORT_TMPL = """
</p>
<table id='result_table'>
<colgroup>
<col align='left' />
<col align='right' />
<col align='right' />
<col align='right' />
<col align='right' />
<col align='right' />
</colgroup>
<tr id='header_row'>
    <td>测试统计</td>
    <td>总数</td>
    <td>通过</td>
    <td>失败</td>
    <td>错误</td>
</tr>
<tr id='total_row'>
    <td>合计</td>
    <td>%(count)s</td>
    <td>%(Pass)s</td>
    <td>%(fail)s</td>
    <td>%(error)s</td>
</tr>
</table>
<br><br>
<table id='result_table'>
<colgroup>
<col align='left' />
<col align='right' />
<col align='right' />
<col align='right' />
<col align='right' />
<col align='right' />
</colgroup>
<tr id='header_row'>
    <td width='140px'>测试用例名称</td>
    <td width='140px'>状态</td>
    <td>详细信息</td>
    <th width='100px'>浏览器</td>
    <td width='100px'>执行时间</td>
</tr>
%(test_list)s
</table>
"""  # variables: (test_list, count, Pass, fail, error)

    REPORT_CLASS_TMPL = r"""
<tr class='%(style)s'>
    <td>%(name)s</td>
    <td>%(status)s</td>
    <td>%(detail)s</td>
    <td>%(drivername)s</td>
    <td>%(exectime)s</td>
</tr>
"""  # variables: (style, desc, count, Pass, fail, error, cid)

    REPORT_TEST_WITH_OUTPUT_TMPL = r"""
<tr id='%(tid)s' class='%(Class)s'>
    <td class='%(style)s'><div class='testcase'>%(desc)s</div></td>
    <td colspan='5' align='center'>

    <!--css div popup start-->
    <a class="popup_link" onfocus='this.blur();' href="javascript:showTestDetail('div_%(tid)s')" >
        %(status)s</a>

    <div id='div_%(tid)s' class="popup_window">
        <div style='text-align: right; color:red;cursor:pointer'>
        <a onfocus='this.blur();' onclick="document.getElementById('div_%(tid)s').style.display = 'none' " >
           [x]</a>
        </div>
        <pre>
        %(script)s
        </pre>
    </div>
    <!--css div popup end-->

    </td>
</tr>
"""  # variables: (tid, Class, style, desc, status)

    REPORT_TEST_NO_OUTPUT_TMPL = r"""
<tr id='%(tid)s' class='%(Class)s'>
    <td class='%(style)s'><div class='testcase'>%(desc)s</div></td>
    <td colspan='5' align='center'>%(status)s</td>
</tr>
"""  # variables: (tid, Class, style, desc, status)

    # ------------------------------------------------------------------------
    # ENDING
    #

    ENDING_TMPL = """<div id='ending'>&nbsp;</div>"""


# -------------------- The end of the Template class -------------------

class TestDetail:
    name = ""
    status = ""
    detail = ""
    exectime = ""
    drivername = ""


class TestResult:
    def __init__(self, title, description):
        self.title = title
        self.description = description
        self.result = []
        self.success_count = 0
        self.failure_count = 0
        self.error_count = 0
        self.ie_success_count = 0
        self.ie_failure_count = 0
        self.ie_error_count = 0
        self.chrome_success_count = 0
        self.chrome_failure_count = 0
        self.chrome_error_count = 0
        self.firefox_success_count = 0
        self.firefox_failure_count = 0
        self.firefox_error_count = 0

    def addTimeInfo(self, startTime, stopTime):
        self.startTime = startTime
        self.stopTime = stopTime

    def addResult(self, name, status, detail, exectime, drivername):
        obj = TestDetail()
        obj.name = name
        obj.status = status
        obj.detail = detail
        obj.exectime = exectime
        obj.drivername = drivername
        if obj.status == "通过":
            self.success_count += 1
            if drivername == 'internet explorer':
                self.ie_success_count += 1
            if drivername == 'chrome':
                self.chrome_success_count += 1
            if drivername == 'firefox':
                self.firefox_success_count += 1
        elif obj.status == "失败":
            self.failure_count += 1
            if drivername == 'internet explorer':
                self.ie_failure_count += 1
            if drivername == 'chrome':
                self.chrome_failure_count += 1
            if drivername == 'firefox':
                self.firefox_failure_count += 1
        else:
            self.error_count += 1
            if drivername == 'internet explorer':
                self.ie_error_count += 1
            if drivername == 'chrome':
                self.chrome_error_count += 1
            if drivername == 'firefox':
                self.firefox_error_count += 1
        self.result.append(obj)


class HTMLReport(Template_mixin):
    """
    """

    def __init__(self, stream, result):
        self.stream = stream
        self.result = result

    def getReportAttr(self):
        startTime = str(self.result.startTime)[:19]
        duration = str(self.result.stopTime - self.result.startTime)
        status = []
        if self.result.success_count: status.append('通过 %s' % self.result.success_count)
        if self.result.failure_count: status.append('失败 %s' % self.result.failure_count)
        if self.result.error_count:   status.append('错误 %s' % self.result.error_count)
        if status:
            status = ' '.join(status)
        else:
            status = 'none'
        return [
            ('开始时间', startTime),
            ('用时', duration),
            ('测试结果', status),
        ]

    def generateReport(self):
        report_attrs = self.getReportAttr()
        stylesheet = self._generate_stylesheet()
        heading = self._generate_heading(report_attrs)
        report = self._generate_report()
        ending = self._generate_ending()
        output = self.HTML_TMPL % dict(
            title=saxutils.escape(self.result.title),
            stylesheet=stylesheet,
            heading=heading,
            report=report,
            ending=ending,
        )
        self.stream.write(output.encode('utf-8'))
        # self.stream.write(output)

    def _generate_stylesheet(self):
        return self.STYLESHEET_TMPL

    def _generate_heading(self, report_attrs):
        a_lines = []
        for name, value in report_attrs:
            line = self.HEADING_ATTRIBUTE_TMPL % dict(
                name=saxutils.escape(name),
                value=saxutils.escape(value),
            )
            a_lines.append(line)
        heading = self.HEADING_TMPL % dict(
            title=saxutils.escape(self.result.title),
            parameters=''.join(a_lines),
            description=saxutils.escape(self.result.description),
        )
        return heading

    def _generate_report(self):
        rows = []
        for item in self.result.result:
            st = "passCase"
            if item.status == "失败":
                st = "failCase"
            elif item.status == "错误":
                st = "errorCase"

            row = self.REPORT_CLASS_TMPL % dict(
                style=st,
                name=item.name,
                status=item.status,
                detail=item.detail,
                exectime=item.exectime,
                drivername=item.drivername
            )
            rows.append(row)

        report = self.REPORT_TMPL % dict(
            test_list=''.join(rows),
            count=str(self.result.success_count + self.result.failure_count + self.result.error_count),
            Pass=str(self.result.success_count),
            fail=str(self.result.failure_count),
            error=str(self.result.error_count),
        )
        return report

    def _generate_ending(self):
        return self.ENDING_TMPL
