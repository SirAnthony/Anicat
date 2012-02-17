#from anime.tests.pages import *
#from anime.tests.errors import *
#from anime.tests.forms import ( RequestsFormsTest, FormsErrorTests,
#            FormsModelErrorTests, FormsDynamicTests, FormsUserTests,
#            FormsFieldsTests, FormsJSONTests )
#from anime.tests.edit import ( EditInitTest, EditDefaultTests,
#            EditSimpleTests, EditRequestsTests, EditAnimebasedTests )
from anime.tests.views import ( AjaxTest, UserViewsTest, EditViewsTest,
            EditViewsRequestsTest, BaseViewsTest, BaseViewsRequestsTest,
            HistoryViewsTest )
#import * - bad

__test__= {
    #'pages': pages,
    #'errors': errors,
    #'forms': forms,
    #'edit': edit,
    'views': views,
}
