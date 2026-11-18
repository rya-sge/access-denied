// European call priced from C++ against libQuantLib (master), plus the Observer
// behaviour: a SimpleQuote change and a RelinkableHandle relink both reprice.
#include <ql/quantlib.hpp>
#include <iomanip>
#include <iostream>

using namespace QuantLib;

int main() {
    Date today(15, January, 2025);
    Settings::instance().evaluationDate() = today;
    DayCounter dc = Actual365Fixed();

    auto spot = ext::make_shared<SimpleQuote>(100.0);
    Handle<YieldTermStructure> r(ext::make_shared<FlatForward>(today, 0.03, dc));
    Handle<YieldTermStructure> q(ext::make_shared<FlatForward>(today, 0.0, dc));
    RelinkableHandle<BlackVolTermStructure> vol(
        ext::make_shared<BlackConstantVol>(today, TARGET(), 0.20, dc));

    auto process = ext::make_shared<BlackScholesMertonProcess>(Handle<Quote>(spot), q, r, vol);
    VanillaOption option(ext::make_shared<PlainVanillaPayoff>(Option::Call, 100.0),
                         ext::make_shared<EuropeanExercise>(today + 1 * Years));
    option.setPricingEngine(ext::make_shared<AnalyticEuropeanEngine>(process));

    std::cout << std::fixed << std::setprecision(5);
    std::cout << "QuantLib " << QL_VERSION << "\n";
    std::cout << "NPV            " << option.NPV() << "  delta " << option.delta() << "\n";
    spot->setValue(105.0);                       // notifies process -> engine -> option
    std::cout << "spot 105       " << option.NPV() << "\n";
    spot->setValue(100.0);
    vol.linkTo(ext::make_shared<BlackConstantVol>(today, TARGET(), 0.25, dc));  // relink
    std::cout << "vol relinked   " << option.NPV() << "\n";
    return 0;
}
