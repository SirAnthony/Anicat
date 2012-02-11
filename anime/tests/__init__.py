#from anime.tests.ajax import *
#from anime.tests.pages import *
#from anime.tests.errors import *
from anime.tests.forms import ( RequestsFormsTest, FormsErrorTests,
            FormsModelErrorTests, FormsDynamicTests, FormsUserTests,
            FormsFieldsTests, FormsJSONTests )
from anime.tests.edit import ( EditInitTest, EditDefaultTests,
            EditSimpleTests, EditRequestsTests, EditAnimebasedTests )
#import * - bad

__test__= {
    #'ajax': ajax,
    #'pages': pages,
    #'errors': errors,
    'forms': forms,
    'edit': edit,
}
